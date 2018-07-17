import logging
from aiohttp import web

logger = logging.getLogger('memority')


class Exit(Exception):
    pass


def error_response(msg, code=200):
    return web.json_response(
        {
            "status": "error",
            "message": msg
        },
        status=code
    )


async def process_request(request: web.Request, handlers: dict, arg: str = 'arg'):
    handler_name = request.match_info.get(arg)

    handler = handlers.get(
        handler_name
    )

    if handler:
        logger.info(handler_name)
        kwargs = await request.json() if request.method == 'POST' else {}
        return web.json_response(
            {
                "status": "success",
                "data": await handler(**kwargs)
            }
        )
    else:
        return web.json_response(
            {
                "status": "error",
                "message": f"unknown {attr}: {handler_name}"
            }
        )
