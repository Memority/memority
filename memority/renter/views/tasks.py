import aiohttp
import asyncio
import contextlib
import logging
import random
from aiohttp import web

from bugtracking import raven_client
from models import HosterFile, Host, HosterFileM2M
from settings import settings
from smart_contracts import memo_db_contract, token_contract
from utils import get_ip, check_if_white_ip
from .base import upload_to_hoster

logger = logging.getLogger('monitoring')


async def get_new_host_for_file(file):
    for hoster in Host.get_queryset_for_uploading_file(file):
        with contextlib.suppress(aiohttp.ClientConnectorError, asyncio.TimeoutError):
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://{hoster.ip}/free-space/', timeout=1) as resp:
                    if resp.status == 200:
                        resp_data = await resp.json()
                        space = resp_data.get('data').get('result')
                        if space >= file.size:
                            return hoster
    else:
        return None


async def upload_file_to_new_host(file: HosterFile, new_host, replacing=None):
    ip = new_host.ip
    logger.info(f'Uploading file to new host | file: {file.hash} | hoster ip: {ip}')
    data = {
        "file_hash": file.hash,
        "owner_key": file.owner_key,
        "signature": file.signature,
        "client_address": file.client_address,
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
            async with session.get(
                    f'http://{host.ip}/files/{hash_}/{host_to_check_address}/status/',
                    timeout=5
            ) as resp:
                resp_data = await resp.json()
                if not resp.status == 200:
                    logger.warning(f'{resp.status} != 200')
                    return None
                status = resp_data.get('data').get('status')
                logger.info(
                    f'Successfully requested file host status '
                    f'| file: {hash_} '
                    f'| host: {host.address} '
                    f'| status: {status}'
                )
                return status
    except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
        logger.warning(f'Error while requesting file host status | file: {hash_} '
                       f'| host: {host.address} | message: {err.__class__.__name__} {str(err)}')
        return None


async def get_file_proof_from_hoster(file_host: HosterFileM2M, from_, to_):
    logger.info(f'Requesting file proof from hoster | file: {file_host.file.hash} | host: {file_host.host.address}')
    ip = file_host.host.ip
    hash_ = file_host.file.hash
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'http://{ip}/files/{hash_}/proof/?from={from_}&to={to_}',
                    timeout=5
            ) as resp:
                if not resp.status == 200:
                    logger.warning(f'{resp.status} != 200')
                    return file_host, None
                resp_data = await resp.json()
                proof = resp_data.get('data').get('hash')
                logger.info(f'Successfully requested file proof '
                            f'| file: {file_host.file.hash} '
                            f'| host: {file_host.host.address}')
                return file_host, proof
    except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
        logger.warning(f'Error while requesting file proof | file: {file_host.file.hash} '
                       f'| host: {file_host.host.address} | message: {err.__class__.__name__} {str(err)}')
        return file_host, None


class TaskView(web.View):

    async def post(self):
        task = self.request.match_info.get('task')
        handler = getattr(self, task)

        if handler:
            return web.json_response(
                {
                    "status": "success",
                    "data": {
                        "result": await handler()
                    }
                },
            )
        else:
            return web.json_response(
                {
                    "status": "error",
                    "message": "unknown task"
                }
            )

    @staticmethod
    async def check_ip():
        ip_from_contract = memo_db_contract.get_host_ip(settings.address)
        if not ip_from_contract:
            return 'Not in hoster list.'

        ok = await check_if_white_ip(ip_from_contract)
        if ok:
            return f'Your IP {ip_from_contract} is OK.'

        logger.warning('Your computer is not accessible by IP from contract!')
        my_ip = await get_ip()
        my_ip = f'{my_ip}:{settings.hoster_app_port}'
        ok = await check_if_white_ip(my_ip)
        if not ok:
            logger.warning('Your computer is not accessible by IP!')
            return 'Your computer is not accessible by IP!'

        if ip_from_contract != my_ip:
            logger.warning(
                f'IP addresses are not equal. Replacing in contract... | '
                f'IP from contract: {ip_from_contract} | '
                f'My IP: {my_ip}'
            )
            await memo_db_contract.add_or_update_host(ip=my_ip, address=settings.address)
            return f'Replaced {ip_from_contract} with {my_ip}'

    async def request_payment_for_file(self):
        data = await self.request.json()
        file = HosterFile.objects.get(id=data.get('file_id'))
        logger.info(f'Requesting payment for file | file: {file.hash}')
        if token_contract.time_to_pay(file.hash):
            logger.info(f'Requesting payment for file | file: {file.hash}')
            amount = await token_contract.request_payout(file.client_address, file.hash)
            logger.info(f'Successfully requested payment for file | file: {file.hash} | amount: {amount}')
            return f'Successfully requested payment for file | file: {file.hash} | amount: {amount}'
        return 'Not time_to_pay'

    async def perform_monitoring_for_file(self):
        data = await self.request.json()
        file = HosterFile.objects.get(id=data.get('file_id'))

        logger.info(f'Started monitoring for file | file: {file.hash}')
        deposit = await file.check_deposit()
        logger.info(f'Deposit: {deposit}')

        file.refresh_from_contract()

        if not file.body_exists:
            logger.info(f'Deleting file (body does not exist) | file: {file.hash}')
            file.delete()
            return f'Deleting file (body does not exist) | file: {file.hash}'

        if settings.address.lower() not in [
            a.lower()
            for a in file.client_contract.get_file_hosts(file.hash)
        ]:
            logger.info(f'Deleting file (i am not in file host list from contract) | file: {file.hash} '
                        f'| {file.client_contract.get_file_hosts(file.hash)} '
                        f'| {settings.address}')
            try:
                1 / 0  # debug; just for sending error message with context
            except ZeroDivisionError:
                raven_client.captureException(extra={
                    "client_contract": file.client_contract.address,
                    "file": file.hash,
                    "host": settings.address,
                    "client_files": str(file.client_contract.get_files())
                })
            file.delete()
            return f'Deleting file (i am not in file host list from contract) | file: {file.hash} ' \
                   f'| {file.client_contract.get_file_hosts(file.hash)} ' \
                   f'| {settings.address}'

        if not await file.check_deposit():
            logger.info(f'No deposit for file | file: {file.hash}')
            file.update_status(HosterFile.WAIT_DEL)
            file.update_no_deposit_counter()
            if file.no_deposit_counter >= 3 * 7:  # 3x monitoring per day, 1 week
                logger.info(f'Deleting file (no deposit) | file: {file.hash}')
                file.delete()
            return f'Deleting file (no deposit) | file: {file.hash}'
        else:
            logger.info(f'Deposit OK | file: {file.hash}')
            file.update_status(HosterFile.ACTIVE)
            file.reset_no_deposit_counter()

        if file.client_contract.need_copy(file.hash):
            logger.info(f'File need copy | file: {file.hash}')
            host = await get_new_host_for_file(file)
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
                continue

            file_host.update_last_ping()
            file_host.update_offline_counter()
            logger.info(
                f'Monitoring: host is offline '
                f'| file: {file.hash} '
                f'| host: {file_host.host.address} '
                f'| offline counter: {file_host.offline_counter}'
            )
            if file_host.offline_counter < 6:
                continue

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
            for _task in done:
                status = _task.result()
                if status == HosterFileM2M.OFFLINE:
                    offline_counter += 1

            logger.info(
                f'Monitoring: host is offline '
                f'| file: {file.hash} '
                f'| host: {file_host.host.address} '
                f'| # of hosts approved: {offline_counter}'
            )
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
                    host = await get_new_host_for_file(file)
                    if host:
                        asyncio.ensure_future(
                            upload_file_to_new_host(
                                new_host=host,
                                file=file,
                                replacing=file_host
                            )
                        )
                    else:
                        logger.error(
                            f'Can not find host for replacing file! '
                            f'| file: {file.hash} '
                            f'| offline host: {file_host.host.address} '
                            f'| host offline counter: {file_host.offline_counter} '
                            f'| approved: {offline_counter}'
                        )
        return 'done.'
