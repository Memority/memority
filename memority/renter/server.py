from aiohttp import web

from .middlewares import *
from .views import *


def create_renter_app():
    app = web.Application(middlewares=[allowed_hosts_middleware, error_middleware])

    app.add_routes([
        web.get('/info/{name}/', view_config),
        web.get('/ping/', lambda _: web.json_response({"status": "success"}, status=200)),
        web.get('/ws/', websocket_handler),

        web.post('/account/{action}/', account),
        web.post('/checks/{check}/', check),
        web.post('/files/{action}/', files),
        web.post('/miner_request/', miner_request),
        web.post('/request_mmr/', request_mmr),
        web.post('/tasks/{task}/', task),
        web.post('/user/{attr}/', user),
        web.post('/host/storage/{action}/', storage),
        web.post('/host/{attr}/', host),

        web.view('/miner/{attr}/', MinerView),
    ])

    return app
