from aiohttp import web

from .app_updates import get_app_updates
from .contract_updates import get_contract_updates
from .sync_status import get_sync_status
from ..utils import process_request


async def check(request: web.Request):
    return await process_request(
        request,
        'check',
        {
            "app_updates": get_app_updates,
            "contract_updates": get_contract_updates,
            "sync_status": get_sync_status,
        }
    )
