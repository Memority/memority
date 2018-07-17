import json
import logging
import os

from memority_api_requests import send_get_enodes_request
from settings import settings
from smart_contracts import create_w3

logger = logging.getLogger('monitoring')


async def update_enodes():
    """
    Sync static nodes with server

    :return:  info message [str]
    """

    w3 = create_w3()
    data = await send_get_enodes_request()

    if data.get('status') == 'error':
        logger.error(f'Updating enodes failed: {data.get("error")}')
        return f'Updating enodes failed: {data.get("error")}'

    enodes = set(data.get('enodes'))
    local_enodes_file = os.path.join(settings.blockchain_dir, 'geth', 'static-nodes.json')
    with open(local_enodes_file, 'r') as f:
        local_enodes = set(json.load(f))

    new_enodes = enodes.difference(local_enodes)

    with open(local_enodes_file, 'w') as f:
        json.dump(list(enodes), f)

    for enode in new_enodes:
        w3.admin.addPeer(enode)

    return 'ok'
