import aiohttp
from aiohttp import web

from settings import settings
from smart_contracts import sign_message, get_enode


def error_response(msg, code=200):
    return web.json_response(
        {
            "status": "error",
            "message": msg
        },
        status=code
    )


async def send_miner_request():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.post(
                'https://api.memority.io/api/app/miner/request',
                json={
                    "address": settings.address,
                    "sig_data": settings.address,
                    "sig": await sign_message(settings.address)
                },
                headers={
                    "Accept": "application/json"
                }
        ) as resp:
            return await resp.json()


async def send_add_enode_request():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        enode = await get_enode()
        async with session.post(
                'https://api.memority.io/api/app/enode',
                json={
                    "address": settings.address,
                    "sig_data": enode,
                    "sig": await sign_message(enode)
                },
                headers={
                    "Accept": "application/json"
                }
        ) as resp:
            return await resp.json()


async def send_get_enodes_request():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get(
                'https://api.memority.io/api/app/enodes',
                headers={
                    "Accept": "application/json"
                }
        ) as resp:
            return await resp.json()


async def send_get_miners_request():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get(
                'https://api.memority.io/api/app/miners',
                headers={
                    "Accept": "application/json"
                }
        ) as resp:
            return await resp.json()
