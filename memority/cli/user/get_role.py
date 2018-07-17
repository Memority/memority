import requests

from ..utils import get_url


async def get_role(args):
    r = requests.post(get_url('/user/role/', port=args.memority_core_port), json={})
    data = r.json()
    if data.get('status') == 'success':
        print(', '.join(data.get('data')))
    else:
        print(f'Error: {data.get("message")}')
