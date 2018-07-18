import requests

from ..utils import get_url, Exit


async def create_account(args):
    print('Creating renter account...')
    resp = requests.post(
        get_url('/account/create/', port=args.memority_core_port),
        json={}
    )
    data = resp.json()
    if data.get('status') == 'success':
        print('Renter account successfully created!')
    else:
        msg = data.get('message')
        raise Exit(f'Account creation failed.\n{msg}')
