from aiohttp import web

from .check_enode import check_enode
from .check_ip import check_ip
from .check_miner_status import check_miner_status
from .perform_monitoring_for_file import perform_monitoring_for_file
from .request_payment_for_file import request_payment_for_file
from .update_enodes import update_enodes
from .update_miner_list import update_miner_list


async def task(request: web.Request):
    task_name = request.match_info.get('task')
    handler = {
        "check_enode": check_enode,
        "check_ip": check_ip,
        "check_miner_status": check_miner_status,
        "perform_monitoring_for_file": perform_monitoring_for_file,
        "request_payment_for_file": request_payment_for_file,
        "update_enodes": update_enodes,
        "update_miner_list": update_miner_list
    }.get(
        task_name
    )

    if handler:
        data = await request.json()
        return web.json_response(
            {
                "status": "success",
                "data": {
                    "result": await handler(data)
                }
            },
        )
    else:
        return web.json_response(
            {
                "status": "error",
                "message": "unknown task"
            }
        )
