import aiohttp
import asyncio
import socket
from collections import namedtuple
from concurrent.futures import FIRST_COMPLETED

Service = namedtuple('Service', ('name', 'url', 'ip_attr'))

SERVICES = (
    Service('ipify', 'https://api.ipify.org?format=json', 'ip'),
    Service('ip-api', 'http://ip-api.com/json', 'query')
)


async def fetch_ip(service):
    async with aiohttp.ClientSession() as session:
        async with session.get(service.url) as response:
            json_response = await response.json()
            ip = json_response[service.ip_attr]

    return ip


async def get_ip():
    futures = [fetch_ip(service) for service in SERVICES]
    done, pending = await asyncio.wait(
        futures,
        return_when=FIRST_COMPLETED
    )

    for future in pending:
        future.cancel()

    return done.pop().result()


def check_if_accessible(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, int(port)))
        res = True
        error = None
    except Exception as err:
        res = False
        error = str(err)
    finally:
        s.close()

    return res, error
