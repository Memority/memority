from aiohttp import web

from bugtracking import raven_client

__all__ = ['error_middleware']


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
    except Exception as ex:
        raven_client.captureException()
        return web.json_response({
            "status": "error",
            "message": f'{ex.__class__.__name__}: {ex}'
        }, status=500)
