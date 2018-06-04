import traceback
from aiohttp import web

from bugtracking import raven_client
from settings import settings


__all__ = ['error_middleware', 'allowed_hosts_middleware']


@web.middleware
async def error_middleware(request, handler):
    # noinspection PyBroadException
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
