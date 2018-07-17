from aiohttp import web

from .create_account import create_account
from .generate_address import generate_address
from .get_address import get_address
from .get_balance import get_balance
from .get_role import get_role
from .get_transactions import get_transactions
from ..utils import process_request


async def user(request: web.Request):
    return await process_request(
        request,
        {
            "address": get_address,
            "role": get_role,
            "transactions": get_transactions,
            "balance": get_balance,
            "generate_address": generate_address,
            "create": create_account,
        }
    )
