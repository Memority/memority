from aiohttp import web

from models import HosterFile
from .utils import logger


async def file_list(request):
    """
    Returns list of hashes of all files, stored by this hoster.

    :param request: web.Request
    :return: web.Response
    """

    logger.info('File list')
    files = HosterFile.list_hashes()

    return web.json_response({
        "status": "success",
        "data": {
            "files": files
        }
    })
