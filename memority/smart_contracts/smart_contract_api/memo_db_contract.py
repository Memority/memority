import contextlib
import logging
from datetime import datetime
from web3.exceptions import BadFunctionCallOutput

from settings import settings
from .base import Contract
from .decorators import ensure_latest_contract_version
from .utils import *

logger = logging.getLogger('memority')


class MemoDBContract(Contract):

    def __init__(self) -> None:
        from smart_contracts.smart_contract_api import token_contract
        super().__init__(
            contract_name='MemoDB',
            gas=4_000_000,
            deploy_args=[token_contract.address]
        )

    @ensure_latest_contract_version
    async def add_or_update_host(self, ip, address=None, wait=True):
        # ToDo: check minTokensForHost
        if not address:
            address = settings.address
        logger.info(f'Adding host to Token contract | ip: {ip} | address: {address}')
        from smart_contracts import token_contract
        await token_contract.refill()
        await unlock_account()
        tx_hash = self.contract.updateHost(ip, transact={'from': address, 'gas': 1_000_000})
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
        with contextlib.suppress(BadFunctionCallOutput):
            tx_count = self.contract.transactionsCount(address)
            for i in range(tx_count):
                from smart_contracts import memo_db_contract
                tx_id = memo_db_contract.contract.transactionsId(address, i)
                tx_from, tx_to, file, date, value = memo_db_contract.contract.transactions(tx_id)
                from smart_contracts import token_contract
                res.append({
                    "from": tx_from,
                    "to": tx_to,
                    "comment": file.strip('\x00'),
                    "date": datetime.fromtimestamp(date).isoformat(),
                    "value": token_contract.wmmr_to_mmr(value)
                })
        return res

    @ensure_latest_contract_version
    async def new_client(self, contract_address):
        await unlock_account()
        tx_hash = self.contract.newClient(
            contract_address,
            transact={'from': settings.address, 'gas': 200_000}
        )
        await wait_for_transaction_completion(tx_hash)

    def get_current_version(self, contract_name):
        try:
            return {
                'MemoDB': self.contract.actualDbVersion,
                'Token': self.contract.actualTokenVersion,
                'Client': self.contract.actualClientVersion,
            }.get(contract_name, lambda: None)()
        except BadFunctionCallOutput:
            return 1000  # old contract; version not specified

    def get_client_contract_address(self, owner):
        return self.contract.clientContract(owner)
