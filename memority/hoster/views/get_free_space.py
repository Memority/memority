from aiohttp import web

from models import HosterFile
from settings import settings


async def get_free_space(request):
    """
    Returns the amount of available disk space.

    :param request: web.Request
    :return: web.Response
    """

    return web.json_response({
        "status": "success",
        "data": {
            "result": settings.disk_space_for_hosting * (1024 ** 3) - HosterFile.get_total_size()
        }
    })
