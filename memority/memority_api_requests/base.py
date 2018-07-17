import aiohttp


async def memority_api_request(url: str, method: str = 'get', post_data: dict = None):
    request_kwargs = {
        "url": url,
        "headers": {
            "Accept": "application/json"
        }
    }

    if method == 'post' and post_data:
        request_kwargs["json"] = post_data

    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
    ) as session:
        async with {
            "get": session.get,
            "post": session.post
        }.get(method, NotImplemented)(**request_kwargs) as resp:
            return await resp.json()
