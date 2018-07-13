import requests

from utils import file_size_human_readable
from ..utils import get_url, Exit


def get_data_by_url(url, port):
    r = requests.get(get_url(url, port))
    data = r.json()
    if data.get('status') == 'error':
        raise Exit(f"Error: {data.get('message')}")
    return data.get('data').get('result')


def get_hoster_ip(port):
    return get_data_by_url('/host/ip/', port)


def get_storage_stats(port):
    return get_data_by_url('/host/storage/', port)


def get_reward_info(port):
    return get_data_by_url('/host/rewards/', port)


async def get_host_status(args):
    ip = get_hoster_ip(args.memority_core_port)
    storage_stats = get_storage_stats(args.memority_core_port)
    total = storage_stats.get('total')
    used = storage_stats.get('used')
    free = total - used
    usage_percent = used / total * 100
    rewards = get_reward_info(args.memority_core_port)
    print('Hosting statistics:')
    print()
    print(f'Hoster ip and port: {ip}')
    print()
    print('Disk usage statistics:')
    print(f'Total: {file_size_human_readable(total)}')
    print(f'Used: {file_size_human_readable(used)} ({usage_percent:.2f}%)')
    print(f'Free: {file_size_human_readable(free)}')
    print()
    print(f'Total reward for hosting: {rewards:.18f} MMR')
