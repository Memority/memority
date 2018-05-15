from aiohttp import web

from bugtracking import raven_client
from .tasks import create_scheduler
from .views import *


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
    except Exception as ex:
        raven_client.captureException()
        return web.json_response({
            "status": "error",
            "message": f'{ex.__class__.__name__}: {ex}'
        }, status=500)


def create_hoster_app():
    app = web.Application(middlewares=[error_middleware])
    app['scheduler'] = create_scheduler()
    app.router.add_get('/files/', file_list)
    app.router.add_post('/files/', create_metadata)
    app.router.add_get('/files/{id}/', get_file)
    app.router.add_put('/files/{id}/', load_body)
    app.router.add_get('/files/{id}/proof/', proof)
    app.router.add_put('/files/{id}/metadata/', final_metadata)
    app.router.add_get('/files/{id}/{host}/status/', file_host_status)

    return app
