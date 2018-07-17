import aiohttp
import platform
from async_lru import alru_cache

from settings import settings


@alru_cache()
async def get_app_updates():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get(
                'https://api.memority.io/api/app/version',
                headers={
                    "Accept": "application/json"
                }
        ) as resp:
            data = await resp.json()
            return {
                "update_available": data.get('latest') > settings.version,
                "download_url": data.get(
                    {
                        'Linux': 'download_linux',
                        'Windows': 'download_windows',
                        'Darwin': 'download_macos'
                    }.get(platform.system())
                )
            }
