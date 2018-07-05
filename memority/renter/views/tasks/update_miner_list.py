import logging

from renter.views.utils import send_get_miners_request
from smart_contracts import unlock_account, create_w3

logger = logging.getLogger('monitoring')


async def update_miner_list(_):
    """
    Update miner list and vote for/off

    :return:  info message [str]
    """
    w3 = create_w3()
    await unlock_account()
    data = await send_get_miners_request()
    if data.get('status') == 'error':
        logger.error(f'Updating miners failed: {data.get("error")}')
        return f'Updating miners failed: {data.get("error")}'

    miners = data.get('miners')
    local_active_miners = w3.manager.request_blocking("clique_getSigners", [])

    for miner, vote in miners.items():
        if vote:
            if miner not in local_active_miners:
                w3.manager.request_blocking("clique_propose", [miner, True])
        else:
            if miner in local_active_miners:
                w3.manager.request_blocking("clique_propose", [miner, False])

    return 'ok'
