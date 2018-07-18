import requests

from ..utils import get_url, Exit


def get_data_by_url(url, port):
    r = requests.post(get_url(url, port), json={})
    data = r.json()
    if data.get('status') == 'error':
        raise Exit(f"Error: {data.get('message')}")
    return data.get('result')


def get_miner_ip(port):
    return get_data_by_url('/miner/ip/', port)


def get_reward_info(port):
    return get_data_by_url('/miner/rewards/', port)


async def get_miner_status(args):
    ip = get_miner_ip(args.memority_core_port)
    rewards = get_reward_info(args.memority_core_port)
    print('Mining statistics:')
    print()
    print(f'miner ip and port: {ip}')
    print()
    print(f'Total reward for mining: {rewards:.18f} MMR')
