from settings import settings
from smart_contracts import memo_db_contract


async def get_ip():
    return memo_db_contract.get_host_ip(settings.address)
