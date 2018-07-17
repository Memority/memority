import requests

from utils import file_size_human_readable
from ..utils import get_url


async def get_file_info(args):
    r = requests.post(
        get_url('/files/info/', port=args.memority_core_port),
        json={
            "file_hash": args.hash
        }
    )
    data = r.json()
    if data.get('status') == 'error':
        print(f'Error: {data.get("message")}')
        return

    file_data = data.get('data')

    def print_(k, v):
        print(f"{k+':':<20} {v}")

    print_('Hash', file_data['hash'])
    print_('Name', file_data['name'])
    print_('Size', file_size_human_readable(file_data['size']))
    print_('Status', file_data['status'])
    print_('Uploaded on', file_data['timestamp'])
    print_('Deposit ends on on', file_data['deposit_ends_on'])
