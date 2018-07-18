from smart_contracts import memo_db_contract


async def get_rewards():
    return sum([
        tx['value']
        for tx in memo_db_contract.get_transactions()
        if tx['comment'] == 'host_reward'
    ])
