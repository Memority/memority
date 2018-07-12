from aiohttp import web

from settings import settings
from smart_contracts import token_contract, memo_db_contract, import_private_key_to_eth, client_contract
from utils import get_ip, check_if_accessible


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
        res = []
        if memo_db_contract.get_host_ip(settings.address):
            res.append('host')
        if settings.client_contract_address:
            res.append('renter')
        mining_status = {
            'active': 'miner',
            'pending': 'pending_miner',
            'sent': 'pending_miner'
        }.get(
            settings.mining_status
        )
        if mining_status:
            res.append(mining_status)
        return res

    async def generate_address(self):
        data = await self.request.json()
        password = data.get('password')
        if password:
            data = await self.request.json()
            password = data.get('password')
            settings.generate_keys(password)
            import_private_key_to_eth(password, settings.private_key)
            return None, 201
        else:
            return 'No password given', 400

    async def create_account(self):
        data = await self.request.json()
        role = data.get('role')
        if role == 'renter':
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
        ok, err = check_if_accessible(ip, settings.hoster_app_port)
        if ok:
            ip_with_port = f'{ip}:{settings.hoster_app_port}'
            await memo_db_contract.add_or_update_host(ip=ip_with_port)
        else:
            return (
                "Your computer is not accessible by IP.\n"
                f"{err}\n"
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
