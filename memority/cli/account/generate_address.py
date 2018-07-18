import getpass
import requests

from ..utils import get_url, Exit


async def generate_address(args):
    password1 = getpass.getpass('Set password for your wallet: ')
    password2 = getpass.getpass('Confirm: ')
    if password1 != password2:
        raise Exit('Passwords don`t match!')
    print('Generating address...')
    r = requests.post(get_url('/account/generate_address/', port=args.memority_core_port), json={"password": password1})
    data = r.json()
    if data.get('status') == 'success':
        print(f'Done! Your address: {data.get("result")}')
    else:
        raise Exit(f'Generating address failed.\n'
                   f'{data.get("message")}')
