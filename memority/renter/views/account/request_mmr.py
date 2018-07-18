import memority_api_requests
from smart_contracts import wait_for_transaction_completion, token_contract
from ..utils import Exit


async def request_mmr(key):
    resp_data = await memority_api_requests.request_mmr(key)

    if resp_data.get('status') == 'success':
        tx = resp_data.get('result').strip()
        await wait_for_transaction_completion(tx)
        return token_contract.get_mmr_balance()
    else:
        raise Exit(resp_data.get('error'))
