from aiohttp import web

from .export_account import export_account
from .import_account import import_account
from ..utils import process_request


async def account(request: web.Request):
    return await process_request(
        request,
        {
            "import": import_account,
            "export": export_account,
        }
    )
