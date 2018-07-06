import requests

from .base import get_url


async def miner_request(args):
    r = requests.post(
        get_url('/miner_request/', port=args.memority_core_port),
        json={}
    )
    data = r.json()
    print(f'The request was successfully sent. Request status: {data.get("request_status")}.')
