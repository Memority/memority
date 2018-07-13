import os

import requests

from ..utils import get_url, Exit


async def set_box_dir(args):
    path = args.path
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    r = requests.post(
        get_url('/change_box_dir/', port=args.memority_core_port),
        json={"box_dir": path}
    )
    data = r.json()
    if data.get('status') == 'success':
        print('Storage path changed successfully!')
    else:
        raise Exit(
            f'Changing storage path failed.\n'
            f'{data.get("message")}'
        )
