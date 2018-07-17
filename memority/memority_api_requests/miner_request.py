from settings import settings
from smart_contracts import sign_message
from .base import memority_api_request


async def send_miner_request():
    return await memority_api_request(
        'https://api.memority.io/api/app/miner/request',
        'post',
        {
            "address": settings.address,
            "sig_data": settings.address,
            "sig": await sign_message(settings.address)
        }
    )
