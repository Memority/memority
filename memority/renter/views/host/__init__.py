from aiohttp import web

from .get_ip import get_ip
from .get_rewards import get_rewards
from .get_storage_info import get_storage_info
from .resize_storage import resize_storage
from .set_storage_path import set_storage_path
from .start import become_a_hoster
from ..utils import process_request


async def host(request: web.Request):
    return await process_request(
        request,
        {
            "ip": get_ip,
            "storage": get_storage_info,
            "rewards": get_rewards,
            "start": become_a_hoster,
        }
    )


async def storage(request: web.Request):
    return await process_request(
        request,
        {
            "resize": resize_storage,
            "set_path": set_storage_path
        }
    )
