import requests

from ..utils import get_url


async def get_address(args):
    r = requests.get(get_url('/info/address/', port=args.memority_core_port))
    data = r.json()
    if data.get('status') == 'success':
        print(data.get('data').get('address'))
