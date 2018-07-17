from settings import settings
from smart_contracts import token_contract

from .base import memority_api_request


async def request_mmr(key):
    return await memority_api_request(
        'https://api.memority.io/api/app/new',
        'post',
        {
            "code": key,
            "address": settings.address,
            "version": token_contract.current_version
        }
    )
