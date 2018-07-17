import logging

from memority_api_requests import send_miner_request, send_add_enode_request
from settings import settings
from smart_contracts import create_w3

logger = logging.getLogger('monitoring')


async def check_miner_status():
    """
    Check status of miner request;
    if active and voted, starts mining.

    :return:  info message [str]
    """
    w3 = create_w3()
    data = await send_miner_request()
    if data.get('status') == 'error':
        logger.error(data.get('error'))
        return f'error: {data.get("error")}'

    request_status = data.get('request_status')

    settings.mining_status = request_status

    if request_status != 'active':
        return 'error: not active'

    if settings.address not in w3.manager.request_blocking("clique_getSigners", []):
        return 'error: not in signers'

    resp_data = await send_add_enode_request()

    w3.miner.start(1)

    if resp_data.get('status') == 'error':
        logger.error(resp_data.get('error'))
        return f'error: {data.get("error")}'

    return 'ok'
