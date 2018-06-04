import contextlib
import json
from aiohttp import web, WSMsgType
from asyncio import CancelledError

from settings import settings
from .download import FileDownloader
from .upload import FileUploader

__all__ = ['websocket_handler']


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    with contextlib.suppress(CancelledError):
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                command = data.get('command')
                try:
                    if command == 'upload':
                        resp = await FileUploader(**data.get('kwargs')).perform_uploading()
                    elif command == 'download':
                        resp = await FileDownloader(**data.get('kwargs')).perform_downloading()
                    else:
                        resp = {
                            "status": "error",
                            "message": f'Invalid command: {command}'
                        }
                except settings.Locked:
                    resp = {
                        "status": "error",
                        "message": 'Account is locked.'
                    }
                except settings.InvalidPassword:
                    resp = {
                        "status": "error",
                        "message": 'Invalid password.'
                    }
                await ws.send_json(resp)

    return ws
