from aiohttp import web
from .request_mmr import request_mmr
from .create_account import create_account
from .export_account import export_account
from .generate_address import generate_address
from .import_account import import_account
from ..utils import process_request


async def account(request: web.Request):
    return await process_request(
        request,
        {
            "import": import_account,
            "export": export_account,
            "generate_address": generate_address,
            "create": create_account,
            "request_mmr": request_mmr,
        }
    )
