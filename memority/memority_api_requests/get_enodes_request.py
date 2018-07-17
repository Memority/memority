from .base import memority_api_request


async def send_get_enodes_request():
    return await memority_api_request(
        'https://api.memority.io/api/app/enodes'
    )
