import pprint

import requests

from .base import get_url


async def list_files(args):
    r = requests.get(
        get_url('/files/', port=args.memority_core_port)
    )
    data = r.json()
    pprint.pprint(data.get('data').get('files'))
