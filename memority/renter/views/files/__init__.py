from aiohttp import web

from .info import file_info
from .list import list_files
from .prolong_deposit import prolong_deposit
from ..utils import process_request


async def files(request: web.Request):
    return await process_request(
        request,
        {
            "list": list_files,
            "info": file_info,
            "prolong_deposit": prolong_deposit,
        }
    )
