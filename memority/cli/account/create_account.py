import contextlib
import getpass
import requests

from ..base import get_url


class Exit(Exception):
    pass


def generate_address(args):
    password1 = getpass.getpass('Set password for your wallet: ')
    password2 = getpass.getpass('Confirm: ')
    if password1 != password2:
        print('Passwords don`t match!')
        raise Exit()
    print('Generating address...')
    r = requests.post(get_url('/user/create/', port=args.memority_core_port), json={"password": password1})
    data = r.json()
    if data.get('status') == 'success':
        print(f'Done! Your address: {data.get("address")}')
    else:
        print(f'Generating address failed.\n'
              f'{data.get("message")}')
        raise Exit()


def request_mmr(args):
    key = input("Paste your Alpha Tester Key here.\n"
                "You can get it after registering on https://memority.io/alpha\n"
                ">> ")
    print('Please wait while we’ll send you MMR tokens for testing, it may take a few minutes.')

    resp = requests.post(
        get_url('/request_mmr/', port=args.memority_core_port),
        json={
            "key": key
        }
    )
    data = resp.json()
    if data.get('status') == 'success':
        print(f'Tokens received. Your balance: {data.get("balance")}')
    else:
        msg = data.get('message')
        print(f'Requesting MMR failed.\n{msg}\nPlease ensure if the key was entered correctly.')
        raise Exit()


def create_account_(args):
    role_n = input("I want to...\n"
                   "1. Store my files\n"
                   "2. Be a hoster\n"
                   "3. Both\n"
                   ">> ")
    if not role_n.isdigit():
        print(f'Invalid choice: {role_n}. Input must be digit.')
        raise Exit()

    role = {
        1: 'renter',
        2: 'host',
        3: 'both'
    }.get(int(role_n), None)

    if not role:
        print(f'Invalid choice: {role_n}')
        raise Exit()

    print(f'Creating account for role "{role}"...\n'
          f'This can take some time, as transaction is being written in blockchain.')

    if role in ['renter', 'both']:
        print('Creating renter account...')
        resp = requests.post(
            get_url('/user/create/', port=args.memority_core_port),
            json={
                "role": 'renter'
            }
        )
        data = resp.json()
        if data.get('status') == 'success':
            print('Client account successfully created!')
        else:
            msg = data.get('message')
            print(f'Account creation failed.\n{msg}')
            raise Exit()
    if role in ['host', 'both']:
        print('Creating hoster account...')
        resp = requests.post(
            get_url('/user/create/', port=args.memority_core_port),
            json={
                "role": 'host'
            }
        )
        data = resp.json()
        if data.get('status') == 'success':
            print('Hoster account successfully created!')
        else:
            msg = data.get('message')
            print(f'Account creation failed.\n{msg}')
            raise Exit()


async def create_account(args):
    with contextlib.suppress(Exit):
        generate_address(args)
        request_mmr(args)
        create_account_(args)
