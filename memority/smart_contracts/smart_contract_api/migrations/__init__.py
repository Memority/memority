from smart_contracts import client_contract
from .from_v0_to_v1000 import Migration0to1000


def get_migration_class(v_from, v_to):
    if v_from == 0:
        if v_to == 1000:
            return Migration0to1000


async def migrate():
    v_from = client_contract.current_version
    v_to = client_contract.highest_local_version
    migration = get_migration_class(v_from=v_from, v_to=v_to)
    if migration:
        await migration().apply()
    else:
        raise Exception(f'No migration for these versions: from {v_from} to {v_to}')
