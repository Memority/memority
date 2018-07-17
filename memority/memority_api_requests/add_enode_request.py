from settings import settings
from smart_contracts import get_enode, sign_message

from .base import memority_api_request


async def send_add_enode_request():
    enode = await get_enode()
    return await memority_api_request(
        'https://api.memority.io/api/app/enode',
        'post',
        {
            "address": settings.address,
            "sig_data": enode,
            "sig": await sign_message(enode)
        }
    )
