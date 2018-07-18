import getpass
import requests

from ..utils import get_url, Exit


def generate_address(args):
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


def request_mmr(args):
    key = input("Paste your Alpha Tester Key here.\n"
                "You can get it after registering on https://memority.io/alpha\n"
                ">> ")
    print('Please wait while we’ll send you MMR tokens for testing, it may take a few minutes.')

    resp = requests.post(
        get_url('/account/request_mmr/', port=args.memority_core_port),
        json={
            "key": key
        }
    )
    data = resp.json()
    if data.get('status') == 'success':
        print(f'Tokens received. Your balance: {data.get("result")}')
    else:
        msg = data.get('message')
        raise Exit(f'Requesting MMR failed.\n{msg}\nPlease ensure if the key was entered correctly.')


def create_account_(args):
    role_n = input("I want to...\n"
                   "1. Store my files\n"
                   "2. Be a hoster\n"
                   "3. Both\n"
                   ">> ")
    if not role_n.isdigit():
        raise Exit(f'Invalid choice: {role_n}. Input must be digit.')

    role = {
        1: 'renter',
        2: 'host',
        3: 'both'
    }.get(int(role_n), None)

    if not role:
        raise Exit(f'Invalid choice: {role_n}')

    print(f'Creating account for role "{role}"...\n'
          f'This can take some time, as transaction is being written in blockchain.')

    if role in ['renter', 'both']:
        print('Creating renter account...')
        resp = requests.post(
            get_url('/account/create/', port=args.memority_core_port),
            json={
                "role": 'renter'
            }
        )
        data = resp.json()
        if data.get('status') == 'success':
            print('Client account successfully created!')
        else:
            msg = data.get('message')
            raise Exit(f'Account creation failed.\n{msg}')
    if role in ['host', 'both']:
        print('Creating hoster account...')
        resp = requests.post(
            get_url('/account/create/', port=args.memority_core_port),
            json={
                "role": 'host'
            }
        )
        data = resp.json()
        if data.get('status') == 'success':
            print('Hoster account successfully created!')
        else:
            msg = data.get('message')
            raise Exit(f'Account creation failed.\n{msg}')


async def create_account(args):
    generate_address(args)
    request_mmr(args)
    create_account_(args)
