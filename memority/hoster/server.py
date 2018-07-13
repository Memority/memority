from aiohttp import web

from .middlewares import error_middleware
from .views import *


def create_hoster_app():
    app = web.Application(middlewares=[error_middleware])
    app.add_routes([
        web.get('/files/', file_list),
        web.get('/files/{id}/', get_file),
        web.get('/files/{id}/proof/', proof),
        web.get('/files/{id}/{host}/status/', file_host_status),
        web.get('/free-space/', get_free_space),
        web.post('/files/', create_metadata),
        web.put('/files/{id}/', load_body),
    ])

    return app
