from smart_contracts import client_contract
from .base import BaseMigration


def get_migration_class(v_from, v_to):
    return BaseMigration  # ToDo: if migration logic changed, select appropriate class based on v_from and v_to


async def migrate():
    v_from = client_contract.current_version
    v_to = client_contract.highest_local_version
    migration = get_migration_class(v_from=v_from, v_to=v_to)
    if migration:
        await migration().apply()
    else:
        raise Exception(f'No migration for these versions: from {v_from} to {v_to}')
