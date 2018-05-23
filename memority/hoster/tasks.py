import asyncio
import contextlib
import logging
import random
from contextlib import redirect_stdout, suppress
from datetime import datetime
from typing import Any

import aiohttp
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from models import HosterFile, HosterFileM2M, Host
from renter.views import upload_to_hoster
from settings import settings
from smart_contracts import token_contract, memo_db_contract
from utils import get_ip

logger = logging.getLogger('monitoring')
logger.write = lambda msg: logger.info(msg) if msg != '\n' else None  # for redirect_stdout


async def request_payment_for_file(file: HosterFile):
    logger.info(f'Requesting payment for file | file: {file.hash}')
    if token_contract.time_to_pay(file.hash):
        if await token_contract.get_deposit(file.client_contract_address, file.hash):
            amount = token_contract.request_payout(file.client_contract_address, file.hash)
            logger.info(f'Successfully requested payment for file | file: {file.hash} | amount: {amount}')


async def request_payment_for_all_files():
    for file in HosterFile.objects.all():
        asyncio.ensure_future(
            request_payment_for_file(file)
        )


async def get_file_proof_from_hoster(file_host: HosterFileM2M, from_, to_) -> (HosterFileM2M, Any):
    logger.info(f'Requesting file proof from hoster | file: {file_host.file.hash} | host: {file_host.host.address}')
    ip = file_host.host.ip
    hash_ = file_host.file.hash
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{ip}/files/{hash_}/proof/?from={from_}&to={to_}') as resp:
                if not resp.status == 200:
                    raise Exception(f'{resp.status} != 200')
                resp_data = await resp.json()
                proof = resp_data.get('data').get('hash')
                logger.info(f'Successfully requested file proof '
                            f'| file: {file_host.file.hash} '
                            f'| host: {file_host.host.address}')
                return file_host, proof
    except Exception as err:
        logger.warning(f'Error while requesting file proof | file: {file_host.file.hash} '
                       f'| host: {file_host.host.address} | message: {err.__class__.__name__} {str(err)}')
        return file_host, None


async def upload_file_to_new_host(file: HosterFile, new_host, replacing=None):
    ip = new_host.ip
    logger.info(f'Uploading file to new host | file: {file.hash} | hoster ip: {ip}')
    data = {
        "file_hash": file.hash,
        "owner_key": file.owner_key,
        "signature": file.signature,
        "client_contract_address": file.client_contract_address,
        "size": file.size,
        "hosts": [host.address for host in file.hosts],
        "replacing": replacing.host.address if replacing else None,
    }
    _, ok = await upload_to_hoster(
        hoster=new_host,
        data=data,
        file=file,
        _logger=logger
    )
    if ok and replacing:
        replacing.delete()
    logger.info(f'Uploaded file to new host | file: {file.hash} | hoster ip: {ip} | ok: {ok}')
    # ToDo: select other host and retry if not ok


async def get_file_status_from_hoster(hash_: str, host_to_check_address: str, host: Host):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{host.ip}/files/{hash_}/{host_to_check_address}/status/') as resp:
                resp_data = await resp.json()
                if not resp.status == 200:
                    raise Exception(f'{resp.status} != 200')
                status = resp_data.get('data').get('status')
                logger.info(f'Successfully requested file host status '
                            f'| file: {hash_} '
                            f'| host: {host.address} '
                            f'| status: {status}')
                return status
    except Exception as err:
        logger.warning(f'Error while requesting file host status | file: {hash_} '
                       f'| host: {host.address} | message: {err.__class__.__name__} {str(err)}')
        return None


async def perform_monitoring_for_file(file: HosterFile):
    logger.info(f'Started monitoring for file | file: {file.hash}')
    deposit = await file.check_deposit()
    logger.info(f'Deposit: {deposit}')

    file.refresh_from_contract()

    if not file.body_exists:
        logger.info(f'Deleting file (body does not exist) | file: {file.hash}')
        file.delete()
        return

    if settings.address.lower() not in [
        a.lower()
        for a in file.client_contract.get_file_hosts(file.hash)
    ]:
        logger.info(f'Deleting file (i am not in file host list from contract) | file: {file.hash}')
        file.delete()
        return

    if not await file.check_deposit():
        logger.info(f'No deposit for file | file: {file.hash}')
        file.update_status(HosterFile.WAIT_DEL)
        file.update_no_deposit_counter()
        if file.no_deposit_counter >= 3 * 7:  # 3x monitoring per day, 1 week
            logger.info(f'Deleting file (no deposit) | file: {file.hash}')
            file.delete()
        return
    else:
        logger.info(f'Deposit OK | file: {file.hash}')
        file.update_status(HosterFile.ACTIVE)
        file.reset_no_deposit_counter()

    if file.client_contract.need_copy(file.hash):
        logger.info(f'File need copy | file: {file.hash}')
        host = Host.get_one_for_uploading_file(file)
        if host:
            await upload_file_to_new_host(
                new_host=host,
                file=file
            )
    file_size = file.size
    from_ = random.randint(0, int(file_size / 2))
    to_ = random.randint(int(file_size / 2), file_size)
    my_proof = await file.compute_chunk_hash(from_, to_)
    logger.info(f'Requesting file proofs | file: {file.hash}')
    if file.hosts:
        done, _ = await asyncio.wait(
            [
                get_file_proof_from_hoster(file_host, from_, to_)
                for file_host in file.file_hosts
            ]
        )
        for task in done:
            file_host, proof = task.result()
            if proof == my_proof:
                file_host.update_last_ping()
                file_host.reset_offline_counter()
                file_host.update_status(HosterFileM2M.ACTIVE)
                logger.info(f'Monitoring OK | file: {file.hash} | host: {file_host.host.address}')
            else:
                file_host.update_last_ping()
                file_host.update_offline_counter()
                logger.info(f'Monitoring: host is offline '
                            f'| file: {file.hash} '
                            f'| host: {file_host.host.address} '
                            f'| offline counter: {file_host.offline_counter}')
                if file_host.offline_counter >= 6:
                    file_host.update_status(HosterFileM2M.OFFLINE)
                    done, _ = await asyncio.wait(
                        [
                            get_file_status_from_hoster(
                                hash_=file.hash,
                                host_to_check_address=file_host.host.address,
                                host=fh.host
                            )
                            for fh in file.file_hosts
                        ]
                    )
                    offline_counter = 1  # <- result from my monitoring
                    for task in done:
                        status = task.result()
                        if status == HosterFileM2M.OFFLINE:
                            offline_counter += 1
                    logger.info(f'Monitoring: host is offline '
                                f'| file: {file.hash} '
                                f'| host: {file_host.host.address} '
                                f'| # of hosts approved: {offline_counter}')
                    if offline_counter > settings.hosters_per_file / 2:
                        logger.info(f'Voting offline | file: {file.hash} | host: {file_host.host.address}')
                        await file.client_contract.vote_offline(
                            address_of_offline=file_host.host.address,
                            file_hash=file.hash
                        )
                        if file.client_contract.need_replace(
                                old_host_address=file_host.host.address,
                                file_hash=file.hash
                        ):
                            logger.info(f'Host need replace | file: {file.hash} | host: {file_host.host.address}')
                            asyncio.ensure_future(
                                upload_file_to_new_host(
                                    new_host=Host.get_one_for_uploading_file(file),
                                    file=file,
                                    replacing=file_host
                                )
                            )


async def make_task(file):
    async def wrapper():
        return await perform_monitoring_for_file(file)

    return wrapper


async def check_ip():
    with contextlib.suppress(settings.Locked):
        ip_from_contract = memo_db_contract.get_host_ip(settings.address)
        if ip_from_contract:
            my_ip = await get_ip()
            my_ip = f'{my_ip}:{settings.hoster_app_port}'
            if ip_from_contract != my_ip:
                logger.warning(f'IP addresses are not equal. Replacing in contract... | '
                               f'IP from contract: {ip_from_contract} | '
                               f'My IP: {my_ip}')
                await memo_db_contract.add_or_update_host(ip=my_ip, address=settings.address)


def get_hour_and_minute_by_number(my_monitoring_number) -> dict:
    minutes_in_8_hrs = 60 * 8
    n = random.randint(0, minutes_in_8_hrs / 10)
    minutes_from_start = my_monitoring_number * (minutes_in_8_hrs / 10) + n
    hour = (datetime.utcnow().hour + (minutes_from_start // 60)) % 24
    minute = minutes_from_start % 60
    return {
        "hour": str(int(hour)),
        "minute": str(int(minute))
    }


async def update_schedule(_scheduler):
    _scheduler.remove_all_jobs()
    for file in HosterFile.objects.all():
        _scheduler.add_job(
            await make_task(file),
            'cron',
            **get_hour_and_minute_by_number(file.my_monitoring_number)
        )
    _scheduler.add_job(
        request_payment_for_all_files,
        'cron',
        week='*',
        day_of_week='0',
        hour='0',
        minute='0'
    )
    _scheduler.add_job(
        asyncio.coroutine(check_ip),
        'cron',
        week='*',
        day_of_week='*',
        hour='*',
        minute='0'
    )
    _scheduler.add_job(
        asyncio.coroutine(_scheduler.update),
        'cron',
        hour='*/8',
    )
    with suppress(SchedulerAlreadyRunningError):
        _scheduler.start()
    with redirect_stdout(logger):
        _scheduler.print_jobs()


def create_scheduler():
    try:
        _scheduler = AsyncIOScheduler()
    except:  # ToDo: specify exception
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _scheduler = AsyncIOScheduler()
    _scheduler.update = lambda: asyncio.ensure_future(update_schedule(_scheduler))
    _scheduler.update()
    return _scheduler


if __name__ == '__main__':
    scheduler = create_scheduler()
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, Exception):
        loop.stop()
        scheduler.shutdown()
