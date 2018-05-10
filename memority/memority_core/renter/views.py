import aiohttp
import asyncio
import contextlib
import logging
import os
from aiohttp import web, ClientConnectorError
from functools import partial
from sqlalchemy.exc import IntegrityError

import smart_contracts
from bugtracking import raven_client
from models import Host, RenterFile
from settings import settings
from smart_contracts import client_contract, token_contract, memo_db_contract, import_private_key_to_eth
from smart_contracts.smart_contract_api import wait_for_transaction_completion
from utils import ask_for_password, check_first_run, DecryptionError, get_ip

# ToDo: review if all these views are required


__all__ = ['upload_file', 'download_file', 'list_files', 'view_config', 'set_disk_space_for_hosting',
           'upload_to_hoster', 'view_user_info', 'create_account', 'unlock', 'import_account', 'export_account',
           'request_mmr']

logger = logging.getLogger('memority')


async def ask_user_for__(details, message, type_):
    return NotImplemented


async def notify_user(message):
    return NotImplemented


def _error_response(msg):
    asyncio.ensure_future(notify_user(msg))
    return {
        "status": "error",
        "message": msg
    }


async def upload_to_hoster(hoster, data, file, _logger=None):
    if not _logger:
        _logger = logger
    ip = hoster.ip
    _logger.info(f'Uploading file metadata to hoster... | file: {file.hash} | hoster ip: {ip}')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'http://{ip}/files/',
                    json=data,
                    timeout=10) as resp1:
                # ToDo: handle 402
                if not resp1.status == 201:
                    return hoster, False
            _logger.info(f'Uploading file body to hoster... | file: {file.hash} | hoster ip: {ip}')
            async with session.put(
                    f'http://{ip}/files/{file.hash}/',
                    data=file.get_filelike()) as resp2:
                if not resp2.status == 200:
                    await session.delete(f'http://{ip}/files/{file.hash}/')
                    return hoster, False
        _logger.info(f'File is uploaded to hoster | file: {file.hash} | hoster ip: {ip}')
        notify_user(f'Uploaded to {hoster.address}')
        return hoster, True
    except (ClientConnectorError, asyncio.TimeoutError) as err:
        _logger.warning(f'Uploading to hoster failed | file: {file.hash} | hoster: {hoster.address} '
                        f'| message: {err.__class__.__name__} {str(err)}')
        return hoster, False
    except Exception as err:
        raven_client.captureException()
        _logger.error(f'Uploading to hoster failed | file: {file.hash} | hoster: {hoster.address} '
                      f'| message: {err.__class__.__name__} {str(err)}')
        return hoster, False


async def upload_file_host_list_to_hoster(hoster, data, file):
    ip = hoster.ip
    logger.info(f'Uploading file host list | file: {file.hash} | hoster ip: {ip}')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                    f'http://{ip}/files/{file.hash}/metadata/',
                    json=data) as resp:
                if not resp.status == 200:
                    resp_data = await resp.read()
                    logger.warning(f'Uploading host list to hoster failed | file: {file.hash} '
                                   f'| hoster: {hoster.address} '
                                   f'| message: {resp_data}')
                    return hoster, False
        logger.info(f'File host list is uploaded | file: {file.hash} | hoster ip: {ip}')
        return hoster, True
    except Exception as err:
        raven_client.captureException()
        logger.warning(f'Uploading host list to hoster failed | file: {file.hash} | hoster: {hoster.address} '
                       f'| message: {err.__class__.__name__} {str(err)}')
        return hoster, False


async def upload_file(**kwargs):
    path = kwargs.get('path', None)
    logger.info(f'Started file uploading | path: {path}')
    await notify_user(f'Started file uploading | path: {path}')
    if not path:
        logger.warning('Path is not specified')
        return _error_response("path is not specified")

    file = await RenterFile.open(path)
    try:
        logger.info(f'Preparing file for uploading | path: {path}')
        await notify_user(f'Preparing file for uploading | path: {path}')
        file.prepare_to_uploading()
    except IntegrityError:
        if file.hash in client_contract.get_files():
            logger.warning(f'The file is already uploaded | path: {path} | hash: {file.hash}')
            return _error_response("The file is already uploaded!")

    if not await token_contract.get_deposit(file_hash=file.hash):
        token_balance = token_contract.get_mmr_balance()
        tokens_to_deposit = await ask_user_for__(
            'tokens_to_deposit',
            'Choose token amount for file deposit\n'
            f'({token_contract.wmmr_to_mmr(token_contract.tokens_per_byte_hour*file.size*10*24*14)} MMR for 2 weeks)',
            type_='float'
        )
        if not tokens_to_deposit:
            return _error_response('Invalid value')
        tokens_to_deposit = float(tokens_to_deposit)
        if tokens_to_deposit > token_balance:
            return _error_response(f'Deposit can not be bigger than your balance.'
                                   f'| mmr balance: {token_balance}')
        await notify_user(f'Creating deposit for file {file.hash}, value: {tokens_to_deposit} MMR...'
                          f'This can take up to 60 seconds, as transaction is being written in blockchain.')
        await client_contract.make_deposit(value=tokens_to_deposit, file_hash=file.hash)

        if not await token_contract.get_deposit(file_hash=file.hash):
            file.delete()
            return _error_response(f'Failed deposit creation | file: {file.hash}')
        await notify_user('Deposit successfully created.')

    file.update_status(RenterFile.UPLOADING)

    # region Upload to 10 hosters
    data = {
        "file_hash": file.hash,
        "owner_key": settings.public_key,
        "signature": file.signature,
        "client_contract_address": settings.client_contract_address,
        "size": file.size
    }

    logger.info('Trying to get hoster list')
    hosters = set(Host.get_n(n=10))
    if not hosters:
        logger.error(f'No hosters available | file: {file.hash}')
        file.delete()
        return _error_response("No hosters available!")
    logger.info(f'Uploading to hosters | file: {file.hash} '
                f'| hosters: {", ".join([hoster.address for hoster in hosters])}')
    await notify_user('Uploading file to hosters')
    hosts_success = set()
    hosts_error = set()
    while True:
        done, _ = await asyncio.wait(
            [
                asyncio.ensure_future(
                    upload_to_hoster(
                        hoster=hoster,
                        data=data,
                        file=file
                    )
                )
                for hoster in hosters
            ]
        )
        for task in done:
            hoster, ok = task.result()
            if ok:
                hosts_success.add(hoster)
            else:
                hosts_error.add(hoster)
        if len(hosts_success) >= 10:
            break
        else:
            logger.info(f'Failed uploading to some hosters | file: {file.hash} '
                        f'| hosters: {", ".join([hoster.address for hoster in hosts_error])}')
            hosters = set(Host.get_n(n=10 - len(hosts_success))) \
                .difference(hosts_success) \
                .difference(hosts_error)
            if not hosters:
                if hosts_success:
                    break
                logger.error(f'No hosters available | file: {file.hash}')
                file.delete()
                return _error_response("No hosters available!")

    hosters = hosts_success

    logger.info(f'Uploaded to hosters | file: {file.hash} '
                f'| hosters: {", ".join([hoster.address for hoster in hosters])}')
    await notify_user('Uploaded.')
    # endregion
    file.update_status(RenterFile.UPLOADED)

    # region Save file metadata to contract
    file_metadata_for_contract = {
        "file_name": file.name,
        "file_size": file.size,
        "signature": file.signature,
        "file_hash": file.hash,
        "hosts": [hoster.address for hoster in hosters]
    }
    try:
        logger.info(f'Sending file metadata to contract | file: {file.hash}')
        await notify_user(f'Sending file metadata to contract | file: {file.hash}...\n'
                          f'This can take up to 60 seconds, as transaction is being written in blockchain.')
        await client_contract.add_hosts(**file_metadata_for_contract)
    except Exception as err:
        raven_client.captureException()
        async with aiohttp.ClientSession() as session:
            for hoster in hosters:
                await session.delete(f'http://{hoster.ip}/files/{file.hash}/')
                logger.info(f'Deleted from hoster | file: {file.hash} | hoster ip: {hoster.ip}')
        file.delete()
        logger.warning(f'Saving data to contract failed | file: {file.hash} '
                       f'| message: {err.__class__.__name__} {str(err)}')
        return _error_response(f'Saving data to contract failed | file: {file.hash} '
                               f'| message: {err.__class__.__name__} {str(err)}')
    # endregion

    # region Upload metadata to all hosters
    logger.info(f'Uploading host list to hosters | file: {file.hash} '
                f'| hosters: {", ".join([hoster.address for hoster in hosters])}')
    await notify_user(f'Uploading host list to hosters | file: {file.hash} '
                      f'| hosters: {", ".join([hoster.address for hoster in hosters])}')
    file_hosters = {
        "hosts": [hoster.address for hoster in hosters]
    }
    done, _ = await asyncio.wait(
        [
            asyncio.ensure_future(
                upload_file_host_list_to_hoster(
                    hoster=hoster,
                    data=file_hosters,
                    file=file
                )
            )
            for hoster in hosters
        ]
    )
    for task in done:
        hoster, ok = task.result()
        if ok:
            print(f'Success: {hoster}')
        else:
            print(f'Error: {hoster}')
    logger.info(f'Uploaded host list to hosters | file: {file.hash} '
                f'| hosters: {", ".join([hoster.address for hoster in hosters])}')
    # endregion

    file.add_hosters(hosters)

    logger.info(f'Finished file uploading | path: {path} | hash: {file.hash}')
    await notify_user(f'Finished file uploading | path: {path} | hash: {file.hash}')

    return {
        "status": "success",
        "details": "uploaded",
        "data": {
            "file": await file.to_json()
        }
    }


async def download_file(**kwargs):
    file_hash = kwargs.get('hash')
    logger.info(f'Started file downloading | file: {file_hash}')
    await notify_user(f'Started file downloading | file: {file_hash}')
    destination = kwargs.get('destination') or settings.default_downloads_dir
    if not file_hash:
        logger.warning('Hash is not specified')
        return _error_response("hash is not specified")

    try:
        file = RenterFile.find(hash_=file_hash)
    except RenterFile.NotFound:
        logger.warning(f'File not found | {file_hash}')
        return _error_response(f"A file with '{file_hash}' hash is not found!")

    file_hosters = file.hosters
    for hoster in file_hosters:
        logger.info(f'Trying to download file... | file: {file_hash} | hoster: {hoster.address}')
        await notify_user(f'Trying to download file... | file: {file_hash} | hoster: {hoster.address}')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://{hoster.ip}/files/{file_hash}/') as response:
                    assert response.status == 200
                    file_body = await response.read()
        except Exception as err:
            logger.warning(f'Downloading from hoster failed | file: {file_hash} | hoster: {hoster.address} '
                           f'| message: {err.__class__.__name__} {str(err)}')
            continue

        file.load_body(file_body)
        logger.info(f'Decrypting file | file: {file_hash} | hoster: {hoster.address}')
        try:
            file.decrypt()
        except DecryptionError:
            if os.getenv('mmr_debug', None):
                import pdb
                pdb.set_trace()
            logger.error(
                f'Failed file decrypting | file: {file_hash} | hoster: {hoster.address}',
                extra={
                    'stack': True,
                }
            )
            continue
        logger.info(f'File successfully downloaded and decrypted | file: {file_hash} | hoster: {hoster.address}')
        await notify_user(f'File successfully downloaded and decrypted | file: {file_hash} | hoster: {hoster.address}')
        break
    else:
        logger.warning(f"Downloading from each of {len(file_hosters)} hosters failed! "
                       f"| file: {file_hash} | hosters: {', '.join([h.address for h in file_hosters])}")
        return _error_response(f"Downloading from each of {len(file_hosters)} hosters failed! "
                               f"| file: {file_hash} | hosters: {', '.join([h.address for h in file_hosters])}")

    try:
        await file.save_to_fs(destination=destination)
    except FileExistsError:
        # ToDo: overwrite existing?
        logger.warning(f'File already exists in filesystem | file: {file_hash}')
        return _error_response("The file already exists! Please specify a different path.")
    except PermissionError as err:
        logger.warning(str(err))
        return _error_response(str(err))

    logger.info(f'Finished file downloading | file: {file_hash}')
    await notify_user(f'Finished file downloading | file: {os.path.join(destination, file.name)}')

    return {
        "status": "success",
        "details": "downloaded",
        "data": {
            "file": {
                "name": os.path.join(destination, file.name)
            }
        }
    }


async def list_files(request):
    if check_first_run():
        return web.json_response({
            "status": "success",
            "details": "file_list",
            "data": {
                "files": []
            }
        })
    RenterFile.refresh_from_contract()
    logger.info('List files')
    await asyncio.sleep(0)  # for await list_files
    return web.json_response({
        "status": "success",
        "details": "file_list",
        "data": {
            "files": await RenterFile.list()
        }
    })


async def view_config(request: web.Request, *args, **kwargs):
    name = request.match_info.get('name')
    if name:
        if name in ['private_key', 'encryption_key']:
            return web.json_response({"status": "error", "details": "forbidden"})
        if name == 'host_ip':
            res = memo_db_contract.get_host_ip(settings.address)
        else:
            res = settings.__getattr__(name)
        if res:
            return web.json_response({
                "status": "success",
                "data": {
                    name: res
                }
            })
        else:
            return web.json_response({"status": "error", "details": "not_found"})

    logger.info('View config')
    config = vars(settings)
    with contextlib.suppress(KeyError):
        config['data'].pop('private_key')
    with contextlib.suppress(KeyError):
        config['data'].pop('encryption_key')
    return web.json_response({
        "status": "success",
        "details": "config",
        "data": {
            "config": config
        }
    })


async def view_user_info(request: web.Request):
    attr = request.match_info.get('attr')
    if attr == 'balance':
        if settings.address:
            res = token_contract.get_mmr_balance()
        else:
            res = None
    elif attr == 'role':
        client, host = None, None
        if memo_db_contract.get_host_ip(settings.address):
            host = True
        if settings.client_contract_address:
            client = True
        if client and host:
            res = 'both'
        elif client:
            res = 'client'
        elif host:
            res = 'host'
        else:
            res = None
    else:
        return web.json_response({"status": "error"})
    return web.json_response({
        "status": "success",
        "data": {
            attr: res
        }
    })


async def create_account(request: web.Request):
    try:
        data = await request.json()
        password = data.get('password')
        if password:
            data = await request.json()
            password = data.get('password')
            settings.generate_keys(password)
            smart_contracts.smart_contract_api.ask_for_password = partial(ask_for_password, password)
            import_private_key_to_eth(password, settings.private_key)
            return web.json_response(
                {"status": "success", "address": settings.address},
                status=201
            )
        role = data.get('role')
        if role == 'client':
            await client_contract.deploy()
        elif role == 'host':
            ip = await get_ip()
            ip = f'{ip}:{settings.hoster_app_port}'
            await memo_db_contract.add_or_update_host(ip=ip)
        elif role == 'both':
            await client_contract.deploy()
            ip = await get_ip()
            ip = f'{ip}:{settings.hoster_app_port}'
            await memo_db_contract.add_or_update_host(ip=ip)
        return web.json_response({"status": "success"}, status=201)
    except:
        # ToDo: cleanup
        raise


async def import_account(request):
    data = await request.json()
    filename = data.get('filename')
    settings.import_account(filename)
    return web.json_response({"status": "success"}, status=200)


async def export_account(request):
    data = await request.json()
    filename = data.get('filename')
    settings.export_account(filename)
    return web.json_response({"status": "success"}, status=200)


async def unlock(request: web.Request):
    data = await request.json()
    password = data.get('password')
    settings.unlock(password)
    smart_contracts.smart_contract_api.ask_for_password = partial(ask_for_password, password)
    global w3
    w3 = smart_contracts.smart_contract_api.create_w3()
    smart_contracts.smart_contract_api.w3 = w3
    client_contract.reload()
    token_contract.reload()
    memo_db_contract.reload()
    if settings.address.lower() not in [a.lower() for a in w3.eth.accounts]:
        import_private_key_to_eth(password=password)
    return web.json_response({"status": "success"})


async def request_mmr(request):
    data = await request.json()
    key = data.get('key')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.post(
                'https://api.memority.io/api/app/new',
                json={
                    "code": key,
                    "address": settings.address
                },
                headers={
                    "Accept": "application/json"
                }
        ) as resp:
            data = await resp.json()
            if data.get('status') == 'success':
                tx = data.get('result').strip()
                await wait_for_transaction_completion(tx)
                return web.json_response(
                    {
                        "status": "success",
                        "balance": token_contract.get_mmr_balance()
                    }
                )
            else:
                return web.json_response(_error_response(data.get('error')))


async def set_disk_space_for_hosting(request: web.Request):
    data = await request.json()
    disk_space = data.get('disk_space')
    settings.disk_space_for_hosting = disk_space
    return web.json_response({"status": "success"})
