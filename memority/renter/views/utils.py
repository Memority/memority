from aiohttp import web


def error_response(msg, code=200):
    return web.json_response(
        {
            "status": "error",
            "message": msg
        },
        status=code
    )


async def process_request(request: web.Request, attr: str, handlers: dict):
    handler_name = request.match_info.get(attr)
    handler = handlers.get(
        handler_name
    )

    if handler:
        kwargs = await request.json() if request.method == 'POST' else {}
        return web.json_response(
            {
                "status": "success",
                "data": {
                    "result": await handler(**kwargs)
                }
            },
        )
    else:
        return web.json_response(
            {
                "status": "error",
                "message": f"unknown {attr}: {handler_name}"
            }
        )

