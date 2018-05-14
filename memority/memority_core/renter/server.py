import contextlib
import json
import renter.views
import traceback
from aiohttp import web, WSMsgType
from asyncio import CancelledError
from bugtracking import raven_client
from functools import partial
from settings import settings
from utils import check_first_run

from .views import *

global STATE
STATE = 0

VIEWS = {
    "upload": upload_file,
    "download": download_file,
}


async def ask_user_for_deposit_size(ws: web.WebSocketResponse, details, data):
    await ws.send_json({
        "status": "action_needed",
        "details": details,
        "data": data
    })
    try:
        resp = await ws.receive_json()
        return resp.get('result')
    except TypeError:
        return None


async def notify_user(ws: web.WebSocketResponse, message):
    await ws.send_json({
        "status": "info",
        "message": message
    })


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    renter.views.ask_user_for_deposit_size = partial(ask_user_for_deposit_size, ws)
    renter.views.notify_user = partial(notify_user, ws)

    with contextlib.suppress(CancelledError):
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                handler = VIEWS.get(data.get('command'), None)
                if handler:
                    try:
                        resp = await handler(**data.get('kwargs', {}))
                    except settings.Locked:
                        resp = {
                            "status": "action_needed",
                            "details": "ask_for_password",
                            "message": 'Account is locked.'
                        }
                    except settings.InvalidPassword:
                        resp = {
                            "status": "action_needed",
                            "message": 'Invalid password.'
                        }
                else:
                    resp = data
                await ws.send_json(resp)

    return ws


async def ping_handler(request):
    return web.json_response({"state": STATE}, status=200)


async def check_first_run_handler(request):
    return web.json_response(
        {
            "status": "success",
            "result": check_first_run()
        },
        status=200
    )


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        return web.json_response({
            "status": "error",
            "message": ex.reason
        }, status=ex.status)
    except settings.Locked:
        return web.json_response({
            "status": "error",
            "message": 'locked'
        }, status=403)
    except settings.InvalidPassword:
        return web.json_response({
            "status": "error",
            "message": 'invalid_password'
        }, status=403)
    except Exception as ex:
        traceback.print_exc()
        raven_client.captureException()
        return web.json_response({
            "status": "error",
            "message": f'{ex.__class__.__name__}: {ex}'
        }, status=500)


@web.middleware
async def allowed_hosts_middleware(request, handler):
    host = request.host
    if ':' in host:
        host = host[:host.rfind(':')]
    if host not in ['127.0.0.1', 'localhost']:
        raise web.HTTPBadRequest

    return await handler(request)


def create_renter_app():
    app = web.Application(middlewares=[allowed_hosts_middleware, error_middleware])
    app.router.add_route('GET', '/', websocket_handler)
    app.router.add_route('GET', '/ping/', ping_handler)
    app.router.add_route('GET', '/files/', list_files)
    app.router.add_route('GET', '/check_first_run/', check_first_run_handler)
    app.router.add_route('GET', '/info/', view_config)
    app.router.add_route('GET', '/info/{name}/', view_config)
    app.router.add_route('GET', '/user/{attr}/', view_user_info)
    app.router.add_route('POST', '/user/create/', create_account)
    app.router.add_route('POST', '/user/import/', import_account)
    app.router.add_route('POST', '/user/export/', export_account)
    app.router.add_route('POST', '/unlock/', unlock)
    app.router.add_route('POST', '/request_mmr/', request_mmr)
    app.router.add_route('POST', '/disk_space/', set_disk_space_for_hosting)
    app.router.add_route('POST', '/change_box_dir/', change_box_dir)
    return app
