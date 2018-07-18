import requests

from ..utils import get_url, Exit


async def request_mmr(args):
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
