from .base import Contract
from .exceptions import ContractNeedsUpdate


def ensure_latest_contract_version(func):
    def wrapper(_contract: Contract, *args, **kwargs):
        if _contract.highest_version > _contract.current_version:
            raise ContractNeedsUpdate(
                f'{_contract.contract_name} '
                f'| current version: {_contract.current_version} '
                f'| update to: {_contract.highest_version} '
            )
        return func(_contract, *args, **kwargs)

    return wrapper
