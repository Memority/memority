from smart_contracts import memo_db_contract


async def get_transactions():
    return memo_db_contract.get_transactions()
