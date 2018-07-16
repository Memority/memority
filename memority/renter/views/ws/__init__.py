import contextlib
import json
from aiohttp import web, WSMsgType
from asyncio import CancelledError

from settings import settings
from .download import FileDownloader
from .upload import FileUploader
from .upgrade_client_contract import ContractUpdater
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
                        resp = await FileUploader(websocket=ws, **data.get('kwargs'))\
                            .perform_uploading()
                    elif command == 'download':
                        resp = await FileDownloader(websocket=ws, **data.get('kwargs'))\
                            .perform_downloading()
                    elif command == 'update_client_contract':
                        resp = await ContractUpdater(websocket=ws)\
                            .perform_updating()
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
                except Exception as err:
                    resp = {
                        "status": "error",
                        "message": str(err)
                    }
                await ws.send_json(resp)

    return ws
