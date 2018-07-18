from settings import settings
from smart_contracts import import_private_key_to_eth
from ..utils import Exit


async def generate_address(password):
    if not password:
        raise Exit('No password given')

    settings.generate_keys(password)
    import_private_key_to_eth(password, settings.private_key)
    return 'ok'
