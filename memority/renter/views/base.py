import aiohttp
import asyncio
import contextlib
import logging
import os
import shutil
from aiohttp import web, ClientConnectorError

from bugtracking import raven_client
from models import RenterFile, HosterFile
from settings import settings
from smart_contracts import client_contract, token_contract, memo_db_contract, import_private_key_to_eth, \
    wait_for_transaction_completion
from smart_contracts.smart_contract_api.utils import create_w3
from utils import check_first_run

__all__ = ['list_files', 'view_config', 'set_disk_space_for_hosting', 'upload_to_hoster', 'request_mmr',
           'change_box_dir', 'file_info', 'update_file_deposit', 'list_transactions', 'sync_status_handler',
           'get_contract_updates']

logger = logging.getLogger('memority')


async def notify_user(message):
    return NotImplemented


def _error_response(msg):
    asyncio.ensure_future(notify_user(msg))
    return {
        "status": "error",
        "message": msg
    }


async def sync_status_handler(request):
    import memority_core
    if not memority_core.SYNC_STARTED:
        data = {
            "syncing": True,
            "percent": -1
        }
    else:
        w3 = create_w3()
        status = w3.eth.syncing
        if status:
            current = status.get('currentBlock')
            highest = status.get('highestBlock')
            percent = int(current / highest * 100)
            data = {
                "syncing": True,
                "percent": percent
            }
        else:
            data = {
                "syncing": False,
                "percent": 100
            }
    return web.json_response({
        "status": "success",
        "data": data
    })


async def upload_to_hoster(hoster, data, file, _logger=None):  # ToDo: mv to hoster
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

                resp_data: dict = await resp1.json()
                if resp_data.get('status') != 'success':
                    raise Exception(
                        f'Uploading metadata failed: {resp_data.get("message")}'
                    )

            _logger.info(f'Uploading file body to hoster... | file: {file.hash} | hoster ip: {ip}')
            async with session.put(
                    f'http://{ip}/files/{file.hash}/',
                    data=file.get_filelike()) as resp2:
                if not resp2.status == 200:
                    import json
                    raise Exception(json.dumps({
                        "status": resp2.status,
                        "response": await resp2.text(),
                        "ip": ip,
                        "hash": file.hash
                    }))
                    # return hoster, False
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


async def file_info(request):
    file_hash = request.match_info.get('file_hash')
    file = RenterFile.objects.get(hash=file_hash)
    return web.json_response({
        "status": "success",
        "data": await file.to_json()
    })


async def update_file_deposit(request: web.Request):
    file_hash = request.match_info.get('file_hash')
    data = await request.json()
    value = data.get('value')
    before = await token_contract.get_deposit(file_hash=file_hash)
    await client_contract.make_deposit(value=value, file_hash=file_hash)
    if not await token_contract.get_deposit(file_hash=file_hash) > before:
        return _error_response('Failed deposit updating.')
    return web.json_response({
        "status": "success",
    })


async def view_config(request: web.Request, *args, **kwargs):
    name = request.match_info.get('name')
    if name:
        if name in ['private_key', 'encryption_key']:
            return web.json_response({"status": "error", "details": "forbidden"})
        if name == 'host_ip':
            res = memo_db_contract.get_host_ip(settings.address)
        elif name == 'space_used':
            res = HosterFile.get_total_size()
            if res < 1024:
                res = f'{res} B'
            elif res < 1024 ** 2:
                res = f'{res / 1024:.2f} KB'
            elif res < 1024 ** 3:
                res = f'{res / 1024 ** 2:.2f} MB'
            else:
                res = f'{res / 1024 ** 3:.2f} GB'
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


async def request_mmr(request):
    data = await request.json()
    key = data.get('key')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.post(
                'https://api.memority.io/api/app/new',
                json={
                    "code": key,
                    "address": settings.address,
                    "version": token_contract.current_version
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


async def change_box_dir(request: web.Request):
    data = await request.json()
    box_dir = os.path.normpath(data.get('box_dir'))
    if box_dir == os.path.normpath(settings.boxes_dir):
        return web.json_response({"status": "success"})
    from_dir = settings.boxes_dir
    for filename in os.listdir(from_dir):
        shutil.move(os.path.join(from_dir, filename), os.path.join(box_dir, filename))
    os.rmdir(from_dir)
    settings.boxes_dir = box_dir
    return web.json_response({"status": "success"})


async def list_transactions(request):
    return web.json_response({
        "status": "success",
        "data": memo_db_contract.get_transactions()
    })


async def get_contract_updates(request):
    try:
        res = client_contract.highest_local_version > client_contract.current_version
    except AttributeError:
        res = False
    return web.json_response({
        "status": "success",
        "data": {
            "result": res
        }
    })
