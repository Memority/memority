import requests

from ..utils import get_url, Exit


async def export_account(args):
    filename = args.destination
    r = requests.post(
        get_url('/account/export/', port=args.memority_core_port),
        json={"filename": filename}
    )
    data = r.json()
    if data.get('status') == 'success':
        print(f'Successfully exported to {filename}')
    else:
        msg = data.get('message')
        raise Exit(f'Exporting account failed.\n{msg}')
