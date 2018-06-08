import asyncio
import logging
from aiohttp import web
from contextlib import redirect_stdout

from smart_contracts import client_contract
from smart_contracts.smart_contract_api.migrations import migrate


class RedirectToWS:

    def __init__(self, func) -> None:
        self.writer = func

    def write(self, message):
        message = message.strip()
        if message and 'pending' not in message:
            try:
                asyncio.ensure_future(self.writer(message))
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())
                asyncio.ensure_future(self.writer(message))


class ContractUpdater:
    class UpdatingError(Exception):
        ...

    def __init__(self, websocket: web.WebSocketResponse) -> None:
        self._websocket = websocket
        self.logger = logging.getLogger('memority')

    async def perform_updating(self):
        try:
            await self.notify_user(
                f'Started updating Smart Contract '
                f'from v{client_contract.current_version} '
                f'to v{client_contract.highest_local_version}, please wait...'
            )
            with redirect_stdout(RedirectToWS(func=self.notify_user)):
                await migrate()

            return {
                "status": "success",
                "details": "client_contract_updated",
            }
        except self.UpdatingError as err:
            return self.error(str(err))

    async def notify_user(self, msg):
        self.logger.info(msg)
        await self._websocket.send_json({
            "status": "info",
            "message": msg
        })

    def error(self, msg):
        self.logger.warning(msg)
        return {
            "status": "error",
            "message": msg
        }
