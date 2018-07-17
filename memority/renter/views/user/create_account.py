from ..utils import Exit
from settings import settings
from smart_contracts import client_contract, memo_db_contract
from utils import get_ip, check_if_accessible


async def create_client_account():
    await client_contract.deploy()


async def create_host_account():
    ip = await get_ip()
    ok, err = check_if_accessible(ip, settings.hoster_app_port)
    if ok:
        ip_with_port = f'{ip}:{settings.hoster_app_port}'
        await memo_db_contract.add_or_update_host(ip=ip_with_port)
    else:
        raise Exit(
            "Your computer is not accessible by IP.\n"
            f"{err}\n"
            "If you are connected via a router, configure port 9378 forwarding "
            "(you can find out how to do this in the manual for your router) and try again.\n"
            "If you can not do it yourself, contact your Internet Service Provider."
        )
    return 'ok'


async def create_account(role):
    if role == 'renter':
        return await create_client_account()

    elif role == 'host':
        return await create_host_account()

    else:
        raise Exit('Unknown role')
