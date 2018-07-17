import requests

from ..utils import get_url, Exit


async def resize_storage(args):
    r = requests.post(
        get_url('/host/storage/resize/', port=args.memority_core_port),
        json={"disk_space": float(args.value)}
    )
    data = r.json()
    if data.get('status') == 'success':
        print('Storage size changed successfully!')
    else:
        raise Exit(
            f'Resizing storage failed.\n'
            f'{data.get("message")}'
        )
