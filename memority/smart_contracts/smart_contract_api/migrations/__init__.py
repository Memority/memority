from smart_contracts import client_contract
from .from_v0_to_v1000 import Migration0to1000
from .from_v0_to_v1010 import Migration0to1010
from .from_v1000_to_v1010 import Migration1000to1010


def get_migration_class(v_from, v_to):
    return {
        0: {
            1000: Migration0to1000,
            1010: Migration0to1010
        },
        1000: {
            1010: Migration1000to1010
        }
    }.get(v_from, {}).get(v_to)


async def migrate():
    v_from = client_contract.current_version
    v_to = client_contract.highest_local_version
    migration = get_migration_class(v_from=v_from, v_to=v_to)
    if migration:
        await migration().apply()
    else:
        raise Exception(f'No migration for these versions: from {v_from} to {v_to}')
