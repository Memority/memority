import requests
from datetime import datetime

from utils import file_size_human_readable
from ..utils import Exit, get_url


def get_file_metadata(file_hash, port):
    r = requests.get(
        get_url(f'/files/{file_hash}/', port=port)
    )
    data = r.json()
    if data.get('status') == 'error':
        raise Exit(f'Error: {data.get("message")}')
    return data.get('data')


def ask_user_for_deposit_value(file_metadata):
    size = file_metadata.get('size')
    price_per_hour = file_metadata.get('price_per_hour')
    deposit_ends_on = datetime.strptime(file_metadata.get('deposit_ends_on', [])[:-4], '%Y-%m-%d %H:%M')
    price_per_2_weeks = price_per_hour * 24 * 14  # 2 weeks
    print('Select the number of MMR you want to add to the deposit.')
    print(f'File name: {file_metadata.get("name")}')
    print(f'File size: {file_size_human_readable(size)}')
    print(f'Deposit ends on {deposit_ends_on.date()}')
    print(f'Price per 2 weeks: {price_per_2_weeks:.18f} MMR')
    value = input('Value to be added to deposit, MMR:\n>> ')
    return value


def prolong_deposit_(file_hash, value, port):
    print(f'Adding {value:.18f} MMR to deposit | file: {file_hash}.\n'
          f'Please wait...')
    r = requests.post(
        get_url(f'/files/{file_hash}/deposit/', port=port),
        json={"value": value}
    )
    data = r.json()
    if data.get('status') == 'success':
        print('File deposit successfully updated.')
    else:
        msg = data.get('message')
        raise Exit(f'Deposit creation failed.\n{msg}')


async def prolong_deposit(args):
    if args.value:
        value = args.value
    else:
        file_metadata = get_file_metadata(args.hash, args.memority_core_port)
        value = ask_user_for_deposit_value(file_metadata)

    try:
        value = float(value)
    except ValueError:
        raise Exit(f'{value} is not a valid number')
    if value <= 0:
        raise Exit('Value must be greater than 0')

    prolong_deposit_(args.hash, value, args.memority_core_port)

    """
    get value
    f'/files/{file_hash}/deposit/',
    {"value": value}
    if data.get('status') == 'success':
        self.finished.emit(
            True, ''
        )
    else:
        msg = data.get('message')
        self.finished.emit(
            False, f'Deposit creation failed.\n{msg}'
        )
    if ok:
        self.refresh_files_tab()
        self.notify('File deposit successfully updated.')
    else:
        self.error(result)
    """
