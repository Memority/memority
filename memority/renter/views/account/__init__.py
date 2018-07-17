from aiohttp import web

from .import_account import import_account
from .export_account import export_account


async def account(request: web.Request):
    action = request.match_info.get('action')
    handler = {
        "import": import_account,
        "export": export_account,
    }.get(
        action
    )

    if handler:
        data = await request.json()
        return web.json_response(
            {
                "status": "success",
                "data": {
                    "result": await handler(data)
                }
            },
        )
    else:
        return web.json_response(
            {
                "status": "error",
                "message": "unknown action"
            }
        )
