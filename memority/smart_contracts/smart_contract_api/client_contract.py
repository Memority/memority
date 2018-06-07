import logging
from web3.exceptions import BadFunctionCallOutput

from bugtracking import raven_client
from settings import settings
from .base import Contract
from .decorators import ensure_latest_contract_version
from .exceptions import ContractNeedsUpdate
from .utils import *

logger = logging.getLogger('memority')


class ClientContract(Contract):

    def __init__(self, address=None) -> None:
        from smart_contracts.smart_contract_api import token_contract
        super().__init__(
            contract_name='Client',
            gas=4_000_000,
            deploy_args=[token_contract.address],
            address=address
        )

    async def deploy(self):
        if self.highest_version > self.highest_local_version:
            raise ContractNeedsUpdate(
                f'{self.contract_name} '
                f'| local version: {self.highest_local_version} '
                f'| update to: {self.highest_version} '
            )
        logger.info(f'Deploying contract | name: {self.contract_name}')
        await unlock_account()

        contract = w3.eth.contract(
            abi=get_contract_abi(self.contract_name),
            bytecode=get_contract_bin(self.contract_name)
        )
        tx_hash = contract.deploy(
            transaction={'from': settings.address, 'gas': self.gas},
            args=self.deploy_args
        )
        await wait_for_transaction_completion(tx_hash)
        lock_account()

        address = get_contract_address_by_tx(tx_hash)
        self.contract = get_contract_instance(self.contract_name, address)

        from smart_contracts.smart_contract_api import memo_db_contract
        await memo_db_contract.new_client(address)

        settings.client_contract_address = address
        settings.client_contract_version = self.current_version

        logger.info(f'Deployed contract | name: {self.contract_name} | address: {address}')

        return address

    @ensure_latest_contract_version
    async def make_deposit(self, value, file_hash):
        """
        :param value: MMR, converted here to wmmr
        :param file_hash: file hash
        :return: None
        """
        from smart_contracts.smart_contract_api import token_contract
        value = token_contract.mmr_to_wmmr(value)
        await token_contract.refill()
        await unlock_account()
        try:
            tx_hash = self.contract.makeDeposit(
                value, file_hash,
                transact={'from': settings.address, 'gas': 1_000_000})
        except Exception:
            raise
        await wait_for_transaction_completion(tx_hash)
        lock_account()

    @ensure_latest_contract_version
    async def add_host_to_file(self, file_hash):
        """
        Called on new host
        :param file_hash: file hash
        :return: None
        """
        from smart_contracts.smart_contract_api import token_contract
        await token_contract.refill()
        await unlock_account()
        tx_hash = self.contract.addHostToFile(
            file_hash,
            transact={'from': settings.address, 'gas': 1_000_000}
        )
        lock_account()
        await wait_for_transaction_completion(tx_hash)

    @ensure_latest_contract_version
    async def vote_offline(self, address_of_offline, file_hash):
        logger.info(f'Vote offline | file: {file_hash} | host: {address_of_offline}')
        from smart_contracts.smart_contract_api import token_contract
        await token_contract.refill()
        await unlock_account()
        self.contract.voteOffline(
            address_of_offline,
            file_hash,
            transact={'from': settings.address, 'gas': 1_000_000}
        )
        lock_account()

    def need_copy(self, file_hash) -> bool:
        return self.contract.needCopy(file_hash)

    def need_replace(self, old_host_address, file_hash) -> bool:
        return self.contract.needReplace(old_host_address, file_hash)

    @ensure_latest_contract_version
    async def new_file(self, file_hash, file_name, file_size, hosts, _,
                       vendor=None, from_address=None):
        if not vendor:
            vendor = settings.address
        if not from_address:
            from_address = settings.address
        logger.info(f'Adding file hosts to Client contract | file: {file_hash} | address: {from_address}')
        from smart_contracts.smart_contract_api import token_contract
        await token_contract.refill()
        await unlock_account()
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

    @ensure_latest_contract_version
    async def replace_host(self, file_hash, old_host_address, from_address=None):
        if not from_address:
            from_address = settings.address
        from smart_contracts.smart_contract_api import token_contract
        await token_contract.refill()
        await unlock_account()
        logger.info(f'Replace file host in Client contract | file: {file_hash} '
                    f'| old: {old_host_address} | new: {from_address}')
        tx_hash = self.contract.replaceHost(
            file_hash,
            old_host_address,
            transact={'from': from_address, 'gas': 1_000_000}
        )
        lock_account()
        await wait_for_transaction_completion(tx_hash)
