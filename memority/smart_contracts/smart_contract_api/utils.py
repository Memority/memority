import asyncio
import json
import logging
import platform
import traceback
from web3 import Web3, IPCProvider, HTTPProvider
from web3.contract import ConciseContract

from bugtracking import raven_client
from settings import settings
from utils import get_ip

__all__ = [
    'ask_for_password',
    'create_w3',
    'get_contract_abi',
    'get_contract_address',
    'get_contract_address_by_tx',
    'get_contract_bin',
    'get_contract_instance',
    'import_private_key_to_eth',
    # 'lock_account',
    'unlock_account',
    'wait_for_transaction_completion',
    'w3',
    'get_enode',
    'sign_message',
]

logger = logging.getLogger('memority')

platform_name = platform.system()


def create_w3():
    if settings.w3_provider == 'ipc':
        _w3 = Web3(IPCProvider(settings.w3_url))
        logger.info(f'Connected to w3 | provider: {settings.w3_provider} | location: {settings.w3_url}')
    elif settings.w3_provider == 'http':
        _w3 = Web3(HTTPProvider(settings.w3_url))
    else:
        raise Exception('Wrong w3_provider!')
    return _w3


w3 = create_w3()


async def wait_for_transaction_completion(tx_hash, max_tries=75):
    while max_tries:
        try:
            tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt:
                status = tx_receipt.get('status')
                if status != 1:
                    logger.error(
                        f'Failed transaction | tx_hash: {tx_hash} | receipt: {tx_receipt}',
                        extra={
                            'stack': True,
                        }
                    )
                    raise Exception(f'Failed transaction | tx_hash: {tx_hash}')
                break
        except ValueError:
            traceback.print_exc()
        print(f'pending transaction {tx_hash}')
        await asyncio.sleep(5)
        max_tries -= 1


def import_private_key_to_eth(password, key=None):
    if not key:
        key = settings.private_key
    w3.personal.importRawKey(key, password)


def get_contract_address_by_tx(tx_hash):
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']
    return contract_address


async def ask_for_password():  # ToDo: del
    try:
        return settings.password
    except AttributeError:
        raise NotImplementedError


async def unlock_account():
    try:
        logger.info(f'Unlocking account | address: {settings.address}')
        password = await ask_for_password()
        address = settings.address
        w3.personal.unlockAccount(address, password)
    except Exception as err:
        raven_client.captureException()
        logger.error(f'Account unlocking failed | address: {settings.address} '
                     f'| exception: {err.__class__.__name__} | message: {str(err)}')
        raise


# def lock_account():
#     w3.personal.lockAccount(settings.address)


def get_contract_address(contract_name):
    if contract_name == 'Client':
        return settings.client_contract_address

    with open(settings.contracts_json, 'r') as f:
        data = json.load(f)
        return data[contract_name][str(max([int(v) for v in data[contract_name].keys()]))]['address']


def get_contract_abi(contract_name, client_latest_version=False):
    with open(settings.contracts_json, 'r') as f:
        data = json.load(f)
    if contract_name == 'Client':
        if client_latest_version:
            version = str(max([int(v) for v in data[contract_name].keys()]))
        else:
            version = str(settings.client_contract_version or 0)
    else:
        version = str(max([int(v) for v in data[contract_name].keys()]))

    return data[contract_name][version]['abi']


def get_contract_bin(contract_name='Client'):
    with open(settings.contracts_json, 'r') as f:
        data = json.load(f)

    version = str(max([int(v) for v in data[contract_name].keys()]))

    return data[contract_name][version]['bin']


def get_contract_instance(contract_name, address=None, client_latest_version=False):
    return w3.eth.contract(
        get_contract_abi(contract_name, client_latest_version=client_latest_version),
        address if address else get_contract_address(contract_name),
        ContractFactoryClass=ConciseContract
    )


async def get_enode():
    await unlock_account()
    node = w3.admin.nodeInfo
    remote_ip = await get_ip()
    enode = "enode://" + node['id'] + "@" + remote_ip + ':' + str(node['ports']['listener'])
    return enode


async def sign_message(message, address=None):
    if not address:
        address = settings.address
    sha = w3.sha3(text=message)
    await unlock_account()
    signature = w3.eth.sign(address, hexstr=sha)
    return signature
