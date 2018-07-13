import logging
from aiohttp import web

logger = logging.getLogger('memority')


def error_response(msg, code=200):
    return web.json_response(
        {
            "status": "error",
            "message": msg
        },
        status=code
    )
