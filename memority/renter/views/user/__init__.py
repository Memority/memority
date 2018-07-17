from aiohttp import web

from .get_address import get_address
from .get_balance import get_balance
from .get_role import get_role
from .get_transactions import get_transactions
from ..utils import process_request


async def user(request: web.Request):
    return await process_request(
        request,
        'attr',
        {
            "address": get_address,
            "role": get_role,
            "transactions": get_transactions,
            "balance": get_balance,
        }
    )
