from aiohttp import web

from models import HosterFileM2M
from .utils import logger, error_response


async def file_host_status(request):
    """
    Given file hash and address of a hoster, returns hoster status for this file.

    :param request: web.Request
    :return: web.Response
    """

    file_hash = request.match_info.get('id')
    host_address = request.match_info.get('host')
    logger.info(f'File host status | file: {file_hash} | host: {host_address}')

    try:
        status = HosterFileM2M.get_status(file_hash, host_address)
    except HosterFileM2M.NotFound:
        msg = f'Hoster file not found | file: {file_hash} | host: {host_address}'
        logger.warning(msg)
        return error_response(msg, code=404)

    return web.json_response({
        "status": "success",
        "data": {
            "status": status
        }
    })
