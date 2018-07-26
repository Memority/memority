import json
import traceback
from aiohttp import web

from bugtracking import raven_client
from settings import settings
from .views.utils import Exit

__all__ = ['error_middleware', 'allowed_hosts_middleware']


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
    except Exit as err:
        return web.json_response({
            "status": "error",
            "message": str(err)
        }, status=400)
    except json.JSONDecodeError as err:
        return web.json_response({
            "status": "error",
            "message": str(err)
        }, status=400)
    except Exception as ex:
        traceback.print_exc()
        sample_rate = 1.0
        if 'No client contract for address' in str(ex):
            sample_rate = .2
        raven_client.captureException(sample_rate=sample_rate)
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
