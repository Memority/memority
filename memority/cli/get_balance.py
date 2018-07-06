import requests

from .base import get_url


async def get_balance(args):
    r = requests.get(get_url('/user/balance/', port=args.memority_core_port))
    data = r.json()
    if data.get('status') == 'success':
        print(data.get('data').get('balance'))
