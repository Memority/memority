import requests
import typing

import utils
from ..base import get_url


async def list_files(args):
    r = requests.get(
        get_url('/files/', port=args.memority_core_port)
    )
    data = r.json()
    files: typing.List[typing.Dict] = data.get('data').get('files')
    if not files:
        print('No files.')
        return

    row = "{:<33}{sep}{:<33}{sep}{:<15}{sep}{:<15}{sep}{:<21}{sep}{:<21}"
    print(row.format('Hash', 'Name', 'Size', 'Status', 'Uploaded on', 'Deposit ends on on', sep='| '))
    print(row.format('-'*33, '-'*33, '-'*15, '-'*15, '-'*21, '-'*21, sep='+-'))
    for file in files:
        print(
            row.format(
                file['hash'],
                file['name'][:32],
                utils.file_size_human_readable(file['size']),
                file['status'],
                file['timestamp'],
                file['deposit_ends_on'],
                sep='| '
            )
        )
