from aiohttp import web
from functools import partial

import smart_contracts
from settings import settings
from smart_contracts import token_contract, memo_db_contract, import_private_key_to_eth, client_contract
from utils import ask_for_password, get_ip, check_if_white_ip


class UserView(web.View):
    async def get(self):
        attr = self.request.match_info.get('attr')
        handler = getattr(self, f'get_{attr}')
        if handler:
            return web.json_response({
                "status": "success",
                "data": {
                    attr: handler()
                }
            })
        else:
            return web.json_response({"status": "error"})

    async def post(self):
        attr = self.request.match_info.get('attr')
        handler = {
            "generate_address": self.generate_address,
            "create": self.create_account,
            "import": self.import_account,
            "export": self.export_account
        }.get(attr, None)

        if handler:
            error_msg, status_code = await handler()
            if not error_msg:
                return web.json_response(
                    {"status": "success"},
                    status=status_code
                )
            else:
                return web.json_response({
                    "status": "error",
                    "message": error_msg
                })
        else:
            return web.json_response({"status": "error"})

    @staticmethod
    def get_balance():
        return token_contract.get_mmr_balance() if settings.address else None

    @staticmethod
    def get_role():
        client, host, res = None, None, None
        if memo_db_contract.get_host_ip(settings.address):
            host = True
        if settings.client_contract_address:
            client = True
        if client and host:
            res = 'both'
        elif client:
            res = 'client'
        elif host:
            res = 'host'
        return res

    async def generate_address(self):
        data = await self.request.json()
        password = data.get('password')
        if password:
            data = await self.request.json()
            password = data.get('password')
            settings.generate_keys(password)
            smart_contracts.smart_contract_api.ask_for_password = partial(ask_for_password, password)
            import_private_key_to_eth(password, settings.private_key)
            return None, 201
        else:
            return 'No password given', 400

    async def create_account(self):
        data = await self.request.json()
        role = data.get('role')
        if role == 'client':
            return await self.create_client_account()
        elif role == 'host':
            return await self.create_host_account()
        else:
            return 'Unknown role', 400

    @staticmethod
    async def create_client_account():
        await client_contract.deploy()
        return None, 201

    @staticmethod
    async def create_host_account():
        ip = await get_ip()
        ip = f'{ip}:{settings.hoster_app_port}'
        ok = await check_if_white_ip(ip)
        if ok:
            await memo_db_contract.add_or_update_host(ip=ip)
        else:
            return (
                "Your computer is not accessible by IP.\n"
                "If you are connected via a router, configure port 9378 forwarding "
                "(you can find out how to do this in the manual for your router) and try again.\n"
                "If you can not do it yourself, contact your Internet Service Provider.",
                400
            )
        return None, 201

    async def import_account(self):
        data = await self.request.json()
        filename = data.get('filename')
        settings.import_account(filename)
        return None, 200

    async def export_account(self):
        data = await self.request.json()
        filename = data.get('filename')
        settings.export_account(filename)
        return None, 200
