from aiohttp import web

from models import HosterFile
from settings import settings
from smart_contracts import memo_db_contract
from .resize_storage import resize_storage
from .set_storage_path import set_storage_path
from ..utils import process_request


async def host(request: web.Request):
    return await process_request(
        request,
        'attr',
        {
            "ip": lambda: memo_db_contract.get_host_ip(settings.address),
            "storage": lambda: {
                "total": settings.disk_space_for_hosting * (1024 ** 3),
                "used": HosterFile.get_total_size()
            },
            "rewards": lambda: sum([
                tx['value']
                for tx in memo_db_contract.get_transactions()
                if tx['comment'] == 'host_reward'
            ]),
        }
    )


async def storage(request: web.Request):
    return await process_request(
        request,
        'action',
        {
            "resize": resize_storage,
            "set_path": set_storage_path
        }
    )
