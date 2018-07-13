import requests


class Exit(Exception):
    pass


def get_url(path, port):
    return f'http://127.0.0.1:{port}{path}'


def get_data_by_url(url, port):
    r = requests.get(get_url(url, port))
    data = r.json()
    if data.get('status') == 'error':
        raise Exit(f"Error: {data.get('message')}")
    return data.get('data')


def check_sync_status(port):
    data = get_data_by_url('/sync_status/', port)
    syncing = data.get('syncing')
    percent = data.get('percent')
    if syncing:
        raise Exit(f"Please wait for the blockchain to sync. "
                   f"Current percentage: {'initialization' if percent == -1 else str(percent)+'%'}.")


def check_app_updates(port):
    data = get_data_by_url('/app_updates/', port)
    update_available = data.get('update_available')
    download_url = data.get('download_url')
    if update_available:
        raise Exit(
            'Application update available!\n'
            f'You can download it on {download_url}'
        )


def check_contract_updates(port):
    update_available = get_data_by_url('/contract_updates/', port).get('result')
    if update_available:
        raise Exit(
            'Smart Contract needs update.\n'
            'Please update it by calling "memority_cli account update_contract"'
        )


def perform_checks(port):
    check_sync_status(port)
    check_app_updates(port)
    check_contract_updates(port)
