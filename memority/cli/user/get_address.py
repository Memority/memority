import requests

from ..utils import get_url


async def get_address(args):
    r = requests.post(get_url('/user/address/', port=args.memority_core_port), json={})
    data = r.json()
    if data.get('status') == 'success':
        print(data.get('data'))
