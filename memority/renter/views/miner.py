import logging
from aiohttp import web

from renter.views.utils import send_miner_request, send_add_enode_request
from settings import settings
from smart_contracts import memo_db_contract, token_contract
from smart_contracts.smart_contract_api.utils import create_w3
from utils import get_ip, check_if_accessible
from .utils import error_response

logger = logging.getLogger('memority')


class MinerError(Exception):
    pass


def _error_response(msg):
    return web.json_response({
        "status": "error",
        "message": msg
    })


async def get_miner_ip():
    ip_from_contract = memo_db_contract.get_host_ip(settings.address)
    if ip_from_contract:
        ip = ip_from_contract.split(':')[0]
    else:
        ip = await get_ip()

    return ip


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


async def miner_request(request):
    try:
        check_balance()

        await check_ip()

        request_status = await send_miner_request_()
        settings.mining_status = request_status

        if request_status == 'active':
            check_if_signer()
            await add_enode()
            start_mining()

        return web.json_response(
            {
                "status": "success",
                "request_status": request_status
            }
        )

    except MinerError as err:
        logger.warning(str(err))
        return _error_response(str(err))


class MinerView(web.View):
    async def get(self):
        if settings.mining_status != 'active':
            return error_response('Not a miner.')

        check_if_signer()

        attr = self.request.match_info.get('attr')
        handler = getattr(self, f'get_{attr}')
        if handler:
            return web.json_response({
                "status": "success",
                "data": {
                    "result": await handler()
                }
            })
        else:
            return error_response(f'Unknown attribute: {attr}')

    @staticmethod
    async def get_ip():
        return await get_miner_ip()

    @staticmethod
    async def get_rewards():
        return sum([
            tx['value']
            for tx in memo_db_contract.get_transactions()
            if tx['comment'] == 'miner_reward'
        ])
