from settings import settings
from smart_contracts import memo_db_contract


async def get_role():
    res = []
    if memo_db_contract.get_host_ip(settings.address):
        res.append('host')
    if settings.client_contract_address:
        res.append('renter')
    mining_status = {
        'active': 'miner',
        'pending': 'pending_miner',
        'sent': 'pending_miner'
    }.get(
        settings.mining_status
    )
    if mining_status:
        res.append(mining_status)
    return res
