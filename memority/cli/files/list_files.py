import requests
import typing

from utils import file_size_human_readable
from ..utils import get_url


async def list_files(args):
    r = requests.post(
        get_url('/files/list/', port=args.memority_core_port), json={}
    )
    data = r.json()
    files: typing.List[typing.Dict] = data.get('data')
    if not files:
        print('No files.')
        return

    row = "{:<33}{sep}{:<33}{sep}{:<15}{sep}{:<17}{sep}{:<21}{sep}{:<21}"
    print(row.format('Hash', 'Name', 'Size', 'Status', 'Uploaded on', 'Deposit ends on on', sep='| '))
    print(row.format('-' * 33, '-' * 33, '-' * 15, '-' * 17, '-' * 21, '-' * 21, sep='+-'))
    for file in files:
        print(
            row.format(
                file['hash'],
                file['name'][:32],
                file_size_human_readable(file['size']),
                file['status'],
                file['timestamp'],
                file['deposit_ends_on'],
                sep='| '
            )
        )
