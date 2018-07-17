from smart_contracts import client_contract


async def get_contract_updates():
    try:
        res = client_contract.highest_local_version > client_contract.current_version
    except AttributeError:
        res = False
    return res
