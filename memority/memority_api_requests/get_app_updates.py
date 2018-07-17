from .base import memority_api_request


async def get_app_updates():
    return await memority_api_request(
        'https://api.memority.io/api/app/version'
    )
