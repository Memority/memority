import requests

from ..utils import get_url


async def get_role(args):
    r = requests.get(get_url('/user/role/', port=args.memority_core_port))
    data = r.json()
    if data.get('status') == 'success':
        print(', '.join(data.get('data').get('role')))
    else:
        print(f'Error: {data.get("message")}')
