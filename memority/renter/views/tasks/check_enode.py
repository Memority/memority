import logging

from memority_api_requests import send_get_enodes_request, send_add_enode_request
from smart_contracts import get_enode

logger = logging.getLogger('monitoring')


async def check_enode():
    """
    Check if the enode address is up-to-date and update if not.

    :return: info message [str]
    """
    enode = await get_enode()
    data = await send_get_enodes_request()

    if data.get('status') == 'error':
        logger.error(f'Updating enodes failed: {data.get("error")}')
        return f'Updating enodes failed: {data.get("error")}'

    enodes = set(data.get('enodes'))
    if enode not in enodes:
        await send_add_enode_request()
        logger.info('Enode updated')
        return 'updated.'

    return 'ok'
