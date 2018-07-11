import requests

from ..base import get_url


async def become_a_hoster(args):
    role = 'host'

    print(f'Creating account for role "{role}"')
    r = requests.post(get_url('/user/create/', port=args.memority_core_port), json={"role": role})
    data = r.json()
    if data.get('status') == 'success':
        print('Account successfully created!')
    else:
        print(f'Account creation failed.\n'
              f'{data.get("message")}')
