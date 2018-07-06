import requests

from .base import get_url


async def miner_request(args):
    r = requests.post(
        get_url('/miner_request/', port=args.memority_core_port),
        json={}
    )
    data = r.json()
    if data.get("status") == 'error':
        print(f'The request was successfully sent. Request status: {data.get("message")}.')

    print(f'The request was successfully sent. Request status: {data.get("request_status")}.')
