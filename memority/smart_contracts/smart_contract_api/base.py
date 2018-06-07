import json
import logging
from web3.exceptions import BadFunctionCallOutput

from settings import settings
from .utils import *

logger = logging.getLogger('memority')
w3 = create_w3()


class Contract:

    def __init__(self, contract_name, gas, deploy_args, address=None) -> None:
        super().__init__()
        self.deploy_args = deploy_args
        self.contract_name = contract_name
        self.gas = gas
        try:
            self.contract = get_contract_instance(contract_name, address)
            self.address = address if address else get_contract_address(self.contract_name)
        except settings.Locked:
            self.contract = None
            self.address = None

    async def deploy(self):
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
        setattr(settings, f'{self.contract_name.lower()}_contract_creation_tx_hash', tx_hash)
        setattr(settings, f'{self.contract_name.lower()}_contract_address', '')
        await wait_for_transaction_completion(tx_hash)
        lock_account()
        address = get_contract_address(self.contract_name)
        self.contract = get_contract_instance(self.contract_name, address)
        logger.info(f'Deployed contract | name: {self.contract_name} | address: {address}')
        return address

    def reload(self):
        try:
            self.address = get_contract_address(self.contract_name)
            self.contract = get_contract_instance(self.contract_name, self.address)
        except settings.Locked:
            self.address = None
            self.contract = None

    @property
    def current_version(self):
        try:
            return self.contract.version()
        except BadFunctionCallOutput:
            return 0  # old contract; version not specified

    @property
    def highest_version(self):
        return memo_db_contract.get_current_version(self.contract_name)

    @property
    def highest_local_version(self):
        with open(settings.contracts_json, 'r') as f:
            data = json.load(f)
        return max([int(v) for v in data[self.contract_name].keys()])
