import aiohttp
import asyncio
import contextlib
import logging
import random

from models import Host
from models import HosterFile, HosterFileM2M
from settings import settings
from ..base import upload_to_hoster

logger = logging.getLogger('monitoring')


class MonitoringError(Exception):
    pass


def ensure_body_exists(file):
    if not file.body_exists:
        logger.info(f'Deleting file (body does not exist) | file: {file.hash}')
        file.delete()
        raise MonitoringError(f'Deleting file (body does not exist) | file: {file.hash}')


def ensure_in_file_hosts(file):
    if settings.address.lower() not in [
        a.lower()
        for a in file.client_contract.get_file_hosts(file.hash)
    ]:
        logger.info(
            f'Deleting file (i am not in file host list from contract) '
            f'| file: {file.hash} '
            f'| {file.client_contract.get_file_hosts(file.hash)} '
            f'| {settings.address}'
        )
        file.delete()
        raise MonitoringError(
            f'Deleting file (i am not in file host list from contract) | file: {file.hash} '
            f'| {file.client_contract.get_file_hosts(file.hash)} '
            f'| {settings.address}'
        )


async def ensure_has_deposit(file):
    if not await file.check_deposit():
        logger.info(f'No deposit for file | file: {file.hash}')
        file.update_status(HosterFile.WAIT_DEL)
        file.update_no_deposit_counter()
        if file.no_deposit_counter >= 3 * 7:  # 3x monitoring per day, 1 week
            logger.info(f'Deleting file (no deposit) | file: {file.hash}')
            file.delete()
            raise MonitoringError(f'Deleting file (no deposit) | file: {file.hash}')
        raise MonitoringError(f'No deposit for file! | file: {file.hash}')
    else:
        logger.info(f'Deposit OK | file: {file.hash}')
        file.update_status(HosterFile.ACTIVE)
        file.reset_no_deposit_counter()


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
    logger.info(
        f'Uploading file to new host '
        f'| file: {file.hash} '
        f'| hoster ip: {ip}'
    )
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
    logger.info(
        f'Uploaded file to new host '
        f'| file: {file.hash} '
        f'| hoster ip: {ip} '
        f'| ok: {ok}'
    )
    # ToDo: select other host and retry if not ok


async def check_if_need_copy(file):
    if file.client_contract.need_copy(file.hash):
        logger.info(f'File need copy | file: {file.hash}')
        host = await get_new_host_for_file(file)
        if host:
            await upload_file_to_new_host(
                new_host=host,
                file=file
            )


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


async def check_file_proofs(file):
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
            logger.info(
                f'Monitoring OK '
                f'| file: {file.hash} '
                f'| host: {file_host.host.address}'
            )
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
                        f'| approved: {offline_counter}',
                        extra={'sample_rate': 0.2}
                    )


async def perform_monitoring_for_file(file_hash):
    """
    Perform monitoring for file

    :return:  info message [str]
    """

    file = HosterFile.objects.get(hash=file_hash)

    logger.info(f'Started monitoring for file | file: {file.hash}')
    deposit = await file.check_deposit()
    logger.info(f'Deposit: {deposit}')

    file.refresh_from_contract()

    try:
        ensure_body_exists(file)
        ensure_in_file_hosts(file)
        await ensure_has_deposit(file)
        await check_if_need_copy(file)
        await check_file_proofs(file)
    except MonitoringError as err:
        return str(err)

    return 'done.'
