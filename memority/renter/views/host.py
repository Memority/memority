from aiohttp import web

from models import HosterFile
from settings import settings
from smart_contracts import memo_db_contract
from .utils import error_response


class HostView(web.View):
    async def get(self):
        if settings.address.lower() \
                not in [h.lower() for h in memo_db_contract.get_hosts()]:
            return error_response('Not a hoster')
        attr = self.request.match_info.get('attr')
        handler = getattr(self, f'get_{attr}')
        if handler:
            return web.json_response({
                "status": "success",
                "data": {
                    "result": handler()
                }
            })
        else:
            return error_response(f'Unknown attribute: {attr}')

    @staticmethod
    def get_ip():
        return memo_db_contract.get_host_ip(settings.address)

    @staticmethod
    def get_storage():
        return {
            "total": settings.disk_space_for_hosting * (1024 ** 3),
            "used": HosterFile.get_total_size()
        }

    @staticmethod
    def get_rewards():
        return sum([
            tx['value']
            for tx in memo_db_contract.get_transactions()
            if tx['comment'] == 'host_reward'
        ])
