from aiohttp import web

from .middlewares import *
from .views import *


def create_renter_app():
    app = web.Application(middlewares=[allowed_hosts_middleware, error_middleware])

    app.add_routes([
        web.get('/ws/', websocket_handler),
        web.get('/check_first_run/', check_first_run_handler),
        web.get('/files/', list_files),
        web.get('/files/{file_hash}/', file_info),
        web.get('/info/', view_config),
        web.get('/info/{name}/', view_config),
        web.get('/ping/', lambda _: web.json_response({"status": "success"}, status=200)),
        web.get('/sync_status/', sync_status_handler),
        web.get('/transactions/', list_transactions),

        web.post('/change_box_dir/', change_box_dir),
        web.post('/disk_space/', set_disk_space_for_hosting),
        web.post('/files/{file_hash}/deposit/', update_file_deposit),
        web.post('/request_mmr/', request_mmr),
        web.post('/unlock/', unlock),

        web.view('/user/{attr}/', UserView)
    ])
    return app
