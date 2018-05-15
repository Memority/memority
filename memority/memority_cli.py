#! /usr/bin/env python

import argparse
import asyncio
import getpass
import json
import os
import pprint

import aiohttp
import requests
from aiohttp import ClientConnectorError

first_run = True


def url(path):
    return f'http://127.0.0.1:{renter_app_port}{path}'


async def send(data_to_send: dict):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(url('/')) as ws:
                await ws.send_json(data_to_send)
                async for msg in ws:
                    data = json.loads(msg.data)
                    status = data.get('status')
                    if status == 'success':
                        if data.get('details') == 'info':
                            print(data.get('message'))
                            continue
                        print(json.dumps(data.get('data'), indent=2))
                        return
                    elif status == 'error':
                        print('Error:')
                        print(data.get('message'))
                        return
                    elif status == 'action_needed':
                        if data.get('details') == 'ask_for_password':
                            password = getpass.getpass()
                            await ws.send_json({'status': 'success', 'password': password})
                            continue
                        else:
                            print(data.get('message'))
                            result = input('>> ')
                            await ws.send_json({'status': 'success', 'result': result})
                            continue

        except ClientConnectorError:
            print('No response from the daemon')


async def task_send(data):
    futures = [send(data)]
    await asyncio.wait(futures)


async def unlock_account(args):
    password = getpass.getpass('Password:')
    r = requests.post(url('/unlock/'), json={"password": password})
    if not r.status_code == 200:
        print('Invalid password!')


async def generate_address(args):
    password1 = getpass.getpass('Set password for your wallet')
    password2 = getpass.getpass('Confirm')
    if password1 != password2:
        print('Passwords don`t match!')
        return
    print('Generating address...')
    r = requests.post(url('/user/create/'), json={"password": password1})
    data = r.json()
    if r.status_code == 201:
        print(f'Done! Your address: {data.get("address")}')
    else:
        print(f'Generating address failed.\n'
              f'{data.get("message")}')


async def create_account(args):
    role_n = input("""
    I want to...
    1. Store my files
    2. Be a hoster
    3. Both
    >> """)
    if not role_n.isdigit():
        print(f'Invalid choice: {role_n}. Input must be digit.')
        return

    role = {
        1: 'client',
        2: 'host',
        3: 'both'
    }.get(int(role_n), None)

    if not role:
        print(f'Invalid choice: {role_n}')
        return

    print(f'Creating account for role "{role}"')
    r = requests.post(url('/user/create/'), json={"role": role})
    if r.status_code == 201:
        print('Account successfully created!')
    else:
        data = r.json()
        print(f'Account creation failed.\n'
              f'{data.get("message")}')


async def become_a_hoster(args):
    role = 'host'

    print(f'Creating account for role "{role}"')
    r = requests.post(url('/user/create/'), json={"role": role})
    if r.status_code == 201:
        print('Account successfully created!')
    else:
        data = r.json()
        print(f'Account creation failed.\n'
              f'{data.get("message")}')


async def get_address(args):
    r = requests.get(url('/info/address/'))
    data = r.json()
    if data.get('status') == 'success':
        print(data.get('data').get('address'))


async def get_balance(args):
    r = requests.get(url('/user/balance/'))
    data = r.json()
    if data.get('status') == 'success':
        print(data.get('data').get('balance'))


async def upload_file(args):
    path = args.path
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    data = {
        "command": "upload",
        "kwargs": {
            "path": path
        }
    }
    return await task_send(data)


async def download_file(args):
    data = {
        "command": "download",
        "kwargs": {
            "hash": args.hash,
            "destination": args.destination
        }
    }
    return await task_send(data)


async def list_files(args):
    r = requests.get(url('/files/'))
    data = r.json()
    pprint.pprint(data.get('data').get('files'))


def parse_args():
    parser = argparse.ArgumentParser(description='Memority CLI')
    parser.add_argument('--renter_app_port', help='Daemon port', type=int, default=9379)
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list_files', help='List files')
    parser_list.set_defaults(func=list_files)

    parser_list = subparsers.add_parser('unlock', help='Unlock')
    parser_list.set_defaults(func=unlock_account)

    parser_list = subparsers.add_parser('generate_address', help='Generate address')
    parser_list.set_defaults(func=generate_address)

    parser_list = subparsers.add_parser('create_account', help='Create account')
    parser_list.set_defaults(func=create_account)

    parser_list = subparsers.add_parser('become_a_hoster', help='Become a hoster')
    parser_list.set_defaults(func=become_a_hoster)

    parser_list = subparsers.add_parser('get_address', help='Get address')
    parser_list.set_defaults(func=get_address)

    parser_list = subparsers.add_parser('get_balance', help='Get balance')
    parser_list.set_defaults(func=get_balance)

    parser_upload = subparsers.add_parser('upload', help='Upload file')
    parser_upload.add_argument('path', help='Path to file')
    parser_upload.set_defaults(func=upload_file)

    parser_download = subparsers.add_parser('download', help='Download file')
    parser_download.add_argument('hash', help='Hash of file')
    parser_download.add_argument('destination', help='Destination')
    parser_download.set_defaults(func=download_file)

    return parser.parse_args()


def main():
    args = parse_args()
    global renter_app_port
    renter_app_port = args.renter_app_port

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(args.func(args))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
