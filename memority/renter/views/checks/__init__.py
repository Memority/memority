from aiohttp import web

from .app_updates import get_app_updates
from .contract_updates import get_contract_updates
from .sync_status import get_sync_status


async def check(request: web.Request):
    check_name = request.match_info.get('check')
    handler = {
        "app_updates": get_app_updates,
        "contract_updates": get_contract_updates,
        "sync_status": get_sync_status,
    }.get(
        check_name
    )

    if handler:
        return web.json_response(
            {
                "status": "success",
                "data": {
                    "result": await handler()
                }
            },
        )
    else:
        return web.json_response(
            {
                "status": "error",
                "message": "unknown check"
            }
        )
