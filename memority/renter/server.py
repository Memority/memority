from aiohttp import web

from .middlewares import *
from .views import *


def create_renter_app():
    app = web.Application(middlewares=[allowed_hosts_middleware, error_middleware])

    app.add_routes([
        web.get('/info/{name}/', view_config),
        web.get('/ping/', lambda _: web.json_response({"status": "success"}, status=200)),
        web.get('/ws/', websocket_handler),

        web.post('/account/{arg}/', account),
        web.post('/checks/{arg}/', check),
        web.post('/files/{arg}/', files),
        web.post('/host/storage/{arg}/', storage),
        web.post('/host/{arg}/', host),
        web.post('/miner/{arg}/', miner),
        web.post('/tasks/{arg}/', task),
        web.post('/user/{arg}/', user),
    ])

    return app
