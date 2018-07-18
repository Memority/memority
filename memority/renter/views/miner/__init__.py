from aiohttp import web

from .get_ip import get_miner_ip
from .get_rewards import get_rewards
from .send_miner_request import miner_request
from ..utils import process_request


async def miner(request: web.Request):
    return await process_request(
        request,
        {
            "ip": get_miner_ip,
            "rewards": get_rewards,
            "request": send_miner_request
        }
    )
