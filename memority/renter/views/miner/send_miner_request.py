import logging
from aiohttp import web

from memority_api_requests import send_miner_request, send_add_enode_request
from settings import settings
from smart_contracts import token_contract
from smart_contracts.smart_contract_api.utils import create_w3
from utils import check_if_accessible
from .get_ip import get_miner_ip
from ..utils import Exit

logger = logging.getLogger('memority')


class MinerError(Exception):
    pass


def check_balance():
    balance = token_contract.get_mmr_balance()
    if balance < settings.min_balance_for_mining:
        raise MinerError(
            f'Your balance is too low for mining. Your balance: {balance}, required: {settings.min_balance_for_mining}'
        )


async def check_ip():
    ip = await get_miner_ip()
    ok, err = check_if_accessible(ip, settings.mining_port)
    if not ok:
        raise MinerError(
            "Your computer is not accessible by IP.\n"
            f"{err}\n"
            f"If you are connected via a router, configure port {settings.mining_port} forwarding "
            "(you can find out how to do this in the manual for your router) and try again.\n"
            "If you can not do it yourself, contact your Internet Service Provider."
        )


def check_if_signer():
    w3 = create_w3()
    if not settings.address.lower() in [
        a.lower()
        for a
        in w3.manager.request_blocking("clique_getSigners", [])
    ]:
        raise MinerError('Approved but not voted yet.')


async def send_miner_request_():
    data = await send_miner_request()
    if data.get('status') == 'error':
        raise MinerError(data.get('error'))

    return data.get('request_status')


async def add_enode():
    resp_data = await send_add_enode_request()
    if resp_data.get('status') == 'error':
        raise MinerError(resp_data.get('error'))


def start_mining():
    logger.info('Starting mining...')
    w3 = create_w3()
    w3.miner.start(1)
    logger.info('Mining started.')


async def miner_request():
    try:
        check_balance()

        await check_ip()

        request_status = await send_miner_request_()
        settings.mining_status = request_status

        if request_status == 'active':
            check_if_signer()
            await add_enode()
            start_mining()

        return request_status

    except MinerError as err:
        logger.warning(str(err))
        raise Exit(str(err))
