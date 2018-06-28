from .client_contract import ClientContract
from .memo_db_contract import MemoDBContract
from .token_contract import TokenContract
from .utils import import_private_key_to_eth, ask_for_password, wait_for_transaction_completion, w3, unlock_account, \
    get_enode, sign_message

__all__ = [
    'token_contract',
    'client_contract',
    'memo_db_contract',
    'import_private_key_to_eth',
    'ask_for_password',
    'wait_for_transaction_completion',
    'ClientContract',
    'w3',
    'unlock_account',
    'get_enode',
    'sign_message',
]

global client_contract
global token_contract
global memo_db_contract

token_contract = TokenContract()
client_contract = ClientContract()
memo_db_contract = MemoDBContract()
