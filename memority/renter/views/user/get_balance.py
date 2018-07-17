from settings import settings
from smart_contracts import token_contract


async def get_balance():
    return token_contract.get_mmr_balance() if settings.address else 0
