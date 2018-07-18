import aiohttp
import asyncio
import logging
from aiohttp import web, ClientConnectorError

from bugtracking import raven_client
from models import HosterFile
from settings import settings
from smart_contracts import memo_db_contract
from utils import file_size_human_readable
from .utils import Exit

__all__ = ['view_config', 'upload_to_hoster']

logger = logging.getLogger('memority')


async def notify_user(message):
    return NotImplemented


def _error_response(msg):
    asyncio.ensure_future(notify_user(msg))
    return {
        "status": "error",
        "message": msg
    }


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
                    raise Exit(
                        f'Uploading metadata failed: {resp_data.get("message")}'
                    )

            _logger.info(f'Uploading file body to hoster... | file: {file.hash} | hoster ip: {ip}')
            async with session.put(
                    f'http://{ip}/files/{file.hash}/',
                    data=file.get_filelike()) as resp2:
                if not resp2.status == 200:
                    import json
                    raise Exit(json.dumps({
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


async def view_config(request: web.Request, *args, **kwargs):
    name = request.match_info.get('name')
    if name in ['private_key', 'encryption_key']:
        return web.json_response({"status": "error", "details": "forbidden"})
    if name == 'host_ip':
        res = memo_db_contract.get_host_ip(settings.address)
    elif name == 'space_used':
        res = file_size_human_readable(HosterFile.get_total_size())
    else:
        res = settings.__getattr__(name)
    if res:
        return web.json_response({
            "status": "success",
            "result": {
                name: res
            }
        })
    else:
        return web.json_response({"status": "error", "details": "not_found"})
