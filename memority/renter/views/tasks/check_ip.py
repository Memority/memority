import logging

from settings import settings
from smart_contracts import memo_db_contract
from utils import get_ip, check_if_accessible

logger = logging.getLogger('monitoring')


async def check_ip():
    """
    Check if IP is equal to IP in contract and update if not
    :return:  info message [str]
    """
    ip_from_contract = memo_db_contract.get_host_ip(settings.address)
    if not ip_from_contract:
        return 'Not in hoster list.'

    ok, err = check_if_accessible(*ip_from_contract.split(':'))
    if ok:
        return f'Your IP {ip_from_contract} is OK.'

    logger.warning(f'Your computer is not accessible by IP from contract! {err}')
    my_ip = await get_ip()
    ok, err = check_if_accessible(my_ip, settings.hoster_app_port)
    if not ok:
        logger.warning(f'Your computer is not accessible by IP! {err}')
        return f'Your computer is not accessible by IP! {err}'

    if ip_from_contract != my_ip:
        logger.warning(
            f'IP addresses are not equal. Replacing in contract... '
            f'| IP from contract: {ip_from_contract} '
            f'| My IP: {my_ip}'
        )
        await memo_db_contract.add_or_update_host(ip=my_ip, address=settings.address)
        return f'Replaced {ip_from_contract} with {my_ip}'
