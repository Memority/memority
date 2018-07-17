import platform
from async_lru import alru_cache

import memority_api_requests
from settings import settings


@alru_cache()
async def get_app_updates():
    data = await memority_api_requests.get_app_updates()
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
