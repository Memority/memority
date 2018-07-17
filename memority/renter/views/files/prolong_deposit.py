from smart_contracts import token_contract, client_contract


async def prolong_deposit(file_hash, value):
    before = await token_contract.get_deposit(file_hash=file_hash)
    await client_contract.make_deposit(value=value, file_hash=file_hash)
    if not await token_contract.get_deposit(file_hash=file_hash) > before:
        raise Exception('Failed deposit updating.')
    return 'ok'
