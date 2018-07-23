from functools import wraps

from .base import Contract
from .exceptions import ContractNeedsUpdate


def ensure_latest_contract_version(func):
    @wraps(func)
    def wrapper(_contract: Contract, *args, **kwargs):
        if _contract.need_update:
            raise ContractNeedsUpdate(
                f'Smart Contract is outdated. Please update the application. '
                f'{_contract.contract_name} '
                f'| current version: {_contract.current_version} '
                f'| update to: {_contract.highest_version} '
            )
        return func(_contract, *args, **kwargs)

    return wrapper


def refresh_contract_on_attribute_error(func):
    @wraps(func)
    def wrapper(_contract: Contract, *args, **kwargs):
        try:
            return func(_contract, *args, **kwargs)
        except AttributeError:
            _contract.reload()
            return func(_contract, *args, **kwargs)

    return wrapper
