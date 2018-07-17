import getpass
import requests

from ..utils import get_url, Exit


async def import_account(args):
    filename = args.file
    password = getpass.getpass()
    r = requests.post(
        get_url('/account/import/', port=args.memority_core_port),
        json={
            "filename": filename,
            "password": password
        }
    )
    data = r.json()
    if data.get('status') == 'success':
        print(f'Successfully imported {filename}')
        print('In order to work correctly with the new account, Memority Core needs to be restarted.')
    else:
        msg = data.get('message')
        raise Exit(f'Importing account failed.\n{msg}')
