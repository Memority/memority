from smart_contracts import client_contract


async def create_account():
    await client_contract.deploy()
    return client_contract.address

