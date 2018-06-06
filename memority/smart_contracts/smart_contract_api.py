import asyncio
import json
import logging
import platform
import traceback
from datetime import datetime
from decimal import Decimal
from web3 import Web3, IPCProvider, HTTPProvider
from web3.contract import ConciseContract
from web3.exceptions import BadFunctionCallOutput

from bugtracking import raven_client
from settings import settings

logger = logging.getLogger('memority')

platform_name = platform.system()

global client_contract
global token_contract
global memo_db_contract


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


def _get_contract_address_by_tx(tx_hash):
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']
    return contract_address


async def ask_for_password():
    raise NotImplementedError


async def _unlock_account():
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


def _lock_account():
    w3.personal.lockAccount(settings.address)


def _get_contract_address(contract_name):
    if settings.__hasattr__(f'{contract_name.lower()}_contract_address'):
        address = getattr(settings, f'{contract_name.lower()}_contract_address')
        if address:
            return address

    if settings.__hasattr__(f'{contract_name.lower()}_contract_creation_tx_hash'):
        tx_hash = getattr(settings, f'{contract_name.lower()}_contract_creation_tx_hash')
        address = _get_contract_address_by_tx(tx_hash)
        if address:
            setattr(settings, f'{contract_name.lower()}_contract_address', address)
            settings.dump()
            return address


def _get_contract_abi(contract_name):
    with open(settings.contracts_json, 'r') as f:
        data = json.load(f)

    version = max([int(v) for v in data[contract_name].keys()])

    return data[contract_name][version]['abi']


def _get_contract_bin(contract_name='Client'):
    with open(settings.contracts_json, 'r') as f:
        data = json.load(f)

    version = max([int(v) for v in data[contract_name].keys()])

    return data[contract_name][version]['bin']


def _get_contract_instance(contract_name, address=None):
    return w3.eth.contract(
        _get_contract_abi(contract_name),
        address if address else _get_contract_address(contract_name),
        ContractFactoryClass=ConciseContract
    )


async def _deploy_contract(contract_name, gas, args):
    await _unlock_account()

    contract = w3.eth.contract(
        abi=_get_contract_abi(contract_name),
        bytecode=_get_contract_bin(contract_name)
    )
    tx_hash = contract.deploy(
        transaction={'from': settings.address, 'gas': gas},
        args=args
    )
    setattr(settings, f'{contract_name.lower()}_contract_creation_tx_hash', tx_hash)
    setattr(settings, f'{contract_name.lower()}_contract_address', '')
    _lock_account()
    return tx_hash


def send_ether(*, from_=None, to, value):
    if not from_:
        from_ = settings.address
    logger.info(f'Sending ether | from: {from_} | to: {to} | value: {value}eth')
    return w3.eth.sendTransaction({"from": from_, "to": to, "value": w3.toWei(value, 'ether'), 'gas': 1_000_000})


class Contract:

    def __init__(self, contract_name, gas, deploy_args, address=None) -> None:
        super().__init__()
        self.deploy_args = deploy_args
        self.contract_name = contract_name
        self.gas = gas
        try:
            self.contract = _get_contract_instance(contract_name, address)
            self.address = address if address else _get_contract_address(self.contract_name)
        except settings.Locked:
            self.contract = None
            self.address = None

    async def deploy(self):
        logger.info(f'Deploying contract | name: {self.contract_name}')
        tx_hash = await _deploy_contract(self.contract_name, self.gas, self.deploy_args)
        await wait_for_transaction_completion(tx_hash)
        address = _get_contract_address(self.contract_name)
        self.contract = _get_contract_instance(self.contract_name, address)
        logger.info(f'Deployed contract | name: {self.contract_name} | address: {address}')
        return address

    def reload(self):
        try:
            self.address = _get_contract_address(self.contract_name)
            self.contract = _get_contract_instance(self.contract_name, self.address)
        except settings.Locked:
            self.address = None
            self.contract = None


class TokenContract(Contract):

    def __init__(self) -> None:
        super().__init__(
            contract_name='Token',
            gas=4_000_000,
            deploy_args=[1000, w3.toWei('0.01', 'ether')]
        )

    def get_token_price(self):
        """
        Price of 1 WMMR
        :return: <int>
        """
        return self.contract.tokenPrice()

    def get_mmr_balance(self, address=None):
        if not address:
            address = settings.address
        try:
            return self.wmmr_to_mmr(self.contract.balanceOf(address))
        except BadFunctionCallOutput:
            return 0

    @staticmethod
    def get_wei_balance(address=None):
        if not address:
            address = settings.address
        return w3.eth.getBalance(address)

    def time_to_pay(self, file_hash) -> bool:
        return self.contract.timeToPay(file_hash)

    async def get_deposit(self, *, owner_contract_address=None, file_hash, ping=False):
        if not owner_contract_address:
            owner_contract_address = settings.client_contract_address
        deposit = self.contract.deposits(owner_contract_address, file_hash)
        if ping and not deposit:
            for i in range(5):
                deposit = self.contract.deposits(owner_contract_address, file_hash)
                if deposit:
                    break
                else:
                    await asyncio.sleep(i * 5)
                    continue
        return deposit

    async def request_payout(self, owner_contract_address, file_hash) -> int:
        await self.refill()
        await _unlock_account()
        amount = self.contract.requestPayout(
            owner_contract_address,
            file_hash,
            transact={'from': settings.address, 'gas': 1_000_000}
        )
        _lock_account()
        # ToDo: payout history to db
        return amount

    def mmr_to_wmmr(self, value):
        return int(Decimal(value) * Decimal(10) ** self.contract.decimals())

    def wmmr_to_mmr(self, value):
        return float(Decimal(value) * Decimal(10) ** -self.contract.decimals())

    @property
    def tokens_per_byte_hour(self):
        return self.contract.tokensPerByteHour()

    async def refill(self):
        if w3.fromWei(w3.eth.getBalance(settings.address), 'ether') < 0.1:
            await _unlock_account()
            tx_hash = self.contract.refill(transact={'from': settings.address, 'gas': 200_000})
            await wait_for_transaction_completion(tx_hash)
            _lock_account()


class MemoDBContract(Contract):

    def __init__(self) -> None:
        super().__init__(
            contract_name='MemoDB',
            gas=4_000_000,
            deploy_args=[token_contract.address]
        )

    async def add_or_update_host(self, ip, address=None, wait=True):
        # ToDo: check minTokensForHost
        if not address:
            address = settings.address
        logger.info(f'Adding host to Token contract | ip: {ip} | address: {address}')
        await token_contract.refill()
        await _unlock_account()
        tx_hash = self.contract.updateHost(ip, transact={'from': address, 'gas': 1_000_000})
        _lock_account()
        if wait:
            await wait_for_transaction_completion(tx_hash)
        logger.info(f'Successfully added host to Token contract | ip: {ip} | address: {address}')

    def get_hosts(self):
        logger.info('Get host list from Token contract')
        return self.contract.getHosts()

    def get_host_ip(self, address):
        if not address:
            return None
        logger.info(f'Get host ip from Token contract | address: {address}')
        try:
            return self.contract.getHostIp(address).strip('\x00')
        except BadFunctionCallOutput:
            return None

    def get_transactions(self, address=None):
        if not address:
            address = settings.address
        if not address:
            return []
        res = []
        tx_count = self.contract.transactionsCount(address)
        for i in range(tx_count):
            tx_id = memo_db_contract.contract.transactionsId(address, i)
            tx_from, tx_to, file, date, value = memo_db_contract.contract.transactions(tx_id)
            res.append({
                "from": tx_from,
                "to": tx_to,
                "comment": file.strip('\x00'),
                "date": datetime.fromtimestamp(date).isoformat(),
                "value": token_contract.wmmr_to_mmr(value)
            })
        return res

    async def new_client(self, contract_address):
        await _unlock_account()
        tx_hash = self.contract.newClient(contract_address)
        await wait_for_transaction_completion(tx_hash)
        _lock_account()


class ClientContract(Contract):

    def __init__(self, address=None) -> None:
        super().__init__(
            contract_name='Client',
            gas=4_000_000,
            deploy_args=[token_contract.address],
            address=address
        )

    async def deploy(self):
        contract_address = await super().deploy()
        await memo_db_contract.new_client(contract_address)
        return contract_address

    async def make_deposit(self, value, file_hash):
        """
        :param value: MMR, converted here to wmmr
        :param file_hash: file hash
        :return: None
        """
        value = token_contract.mmr_to_wmmr(value)
        await token_contract.refill()
        await _unlock_account()
        try:
            tx_hash = self.contract.makeDeposit(
                value, file_hash,
                transact={'from': settings.address, 'gas': 1_000_000})
        except Exception:
            raise
        await wait_for_transaction_completion(tx_hash)
        _lock_account()

    async def add_host_to_file(self, file_hash):
        """
        Called on new host
        :param file_hash: file hash
        :return: None
        """
        await token_contract.refill()
        await _unlock_account()
        tx_hash = self.contract.addHostToFile(
            file_hash,
            transact={'from': settings.address, 'gas': 1_000_000}
        )
        _lock_account()
        await wait_for_transaction_completion(tx_hash)

    async def vote_offline(self, address_of_offline, file_hash):
        logger.info(f'Vote offline | file: {file_hash} | host: {address_of_offline}')
        await token_contract.refill()
        await _unlock_account()
        self.contract.voteOffline(
            address_of_offline,
            file_hash,
            transact={'from': settings.address, 'gas': 1_000_000}
        )
        _lock_account()

    def need_copy(self, file_hash) -> bool:
        return self.contract.needCopy(file_hash)

    def need_replace(self, old_host_address, file_hash) -> bool:
        return self.contract.needReplace(old_host_address, file_hash)

    async def new_file(self, file_hash, file_name, file_size, hosts, signature,
                       vendor=None, from_address=None):
        if not vendor:
            vendor = settings.address
        if not from_address:
            from_address = settings.address
        logger.info(f'Adding file hosts to Client contract | file: {file_hash} | address: {from_address}')
        await token_contract.refill()
        await _unlock_account()
        tx_hash = self.contract.newFile(
            file_hash,
            file_name,
            file_size,
            vendor,
            hosts,
            transact={'from': from_address, 'gas': 1_000_000}
        )
        logger.info(f'Added file hosts to Client contract | file: {file_hash} | address: {from_address}')
        await wait_for_transaction_completion(tx_hash)

    def get_files(self):
        logger.info('Get file list from Client contract')
        return self.contract.getFiles()

    def get_file_name(self, file_hash):
        logger.info(f'Get file name from Client contract | file: {file_hash}')
        return self.contract.getFileName(file_hash)

    def get_file_size(self, file_hash):
        logger.info(f'Get file size from Client contract | file: {file_hash}')
        try:
            return self.contract.getFileSize(file_hash)
        except BadFunctionCallOutput:
            return 0

    def get_file_hosts(self, file_hash):
        logger.info(f'Get file hosts from Client contract | file: {file_hash}')
        try:
            return self.contract.getFileHosts(file_hash)
        except BadFunctionCallOutput:
            raven_client.captureException(extra={
                "client_contract": self.address,
                "file": file_hash,
                "host": settings.address,
                "sync_status": str(create_w3().eth.syncing),
                "client_files": str(self.get_files())
            })
            return []

    async def replace_host(self, file_hash, old_host_address, from_address=None):
        if not from_address:
            from_address = settings.address
        await token_contract.refill()
        await _unlock_account()
        logger.info(f'Replace file host in Client contract | file: {file_hash} '
                    f'| old: {old_host_address} | new: {from_address}')
        tx_hash = self.contract.replaceHost(
            file_hash,
            old_host_address,
            transact={'from': from_address, 'gas': 1_000_000}
        )
        _lock_account()
        await wait_for_transaction_completion(tx_hash)


token_contract = TokenContract()
client_contract = ClientContract()
memo_db_contract = MemoDBContract()
