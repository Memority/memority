import asyncio
from decimal import Decimal
from web3.exceptions import BadFunctionCallOutput

from settings import settings
from .base import Contract, w3
from .utils import *


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
        await unlock_account()
        amount = self.contract.requestPayout(
            owner_contract_address,
            file_hash,
            transact={'from': settings.address, 'gas': 1_000_000}
        )
        lock_account()
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
            await unlock_account()
            tx_hash = self.contract.refill(transact={'from': settings.address, 'gas': 200_000})
            await wait_for_transaction_completion(tx_hash)
            lock_account()
