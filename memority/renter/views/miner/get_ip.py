from settings import settings
from smart_contracts import memo_db_contract
from utils import get_ip


async def get_miner_ip():
    ip_from_contract = memo_db_contract.get_host_ip(settings.address)
    if ip_from_contract:
        ip = ip_from_contract.split(':')[0]
    else:
        ip = await get_ip()

    return f'{ip}:{settings.mining_port}'
