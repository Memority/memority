from aiohttp import web

from .middlewares import *
from .views import *


def create_renter_app():
    app = web.Application(middlewares=[allowed_hosts_middleware, error_middleware])

    app.add_routes([
        web.get('/info/{name}/', view_config),
        web.get('/ping/', lambda _: web.json_response({"status": "success"}, status=200)),
        web.get('/transactions/', list_transactions),
        web.get('/ws/', websocket_handler),

        web.post('/account/{action}/', account),
        web.post('/change_box_dir/', change_box_dir),
        web.post('/checks/{check}/', check),
        web.post('/disk_space/', set_disk_space_for_hosting),
        web.post('/files/{action}/', files),
        web.post('/miner_request/', miner_request),
        web.post('/request_mmr/', request_mmr),
        web.post('/tasks/{task}/', task),

        web.view('/host/{attr}/', HostView),
        web.view('/miner/{attr}/', MinerView),
        web.view('/user/{attr}/', UserView),
    ])

    return app
