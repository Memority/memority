import requests

from handlers import error_handler
from settings import settings
from bugtracking import raven_client

__all__ = ['unlock_account', 'get_user_role', 'get_address', 'get_balance', 'get_token_price', 'get_host_ip',
           'create_account', 'generate_address', 'set_disk_space_for_hosting', 'get_disk_space_for_hosting',
           'import_account', 'export_account', 'request_mmr', 'get_space_used', 'get_box_gir', 'change_box_dir']


def unlock_account(_password):
    r = requests.post(f'{settings.daemon_address}/unlock/', json={"password": _password})
    if not r.status_code == 200:
        error_handler('Invalid password!')
        return False
    return True


async def fetch(address, session):
    async with session.get(f'{settings.daemon_address}{address}') as result:
        return await result.json()


async def get_user_role(session):
    result = await fetch('/user/role/', session)
    if result.get('status') == 'success':
        return result.get('data').get('role')


async def get_address(session):
    result = await fetch('/info/address/', session)
    if result.get('status') == 'success':
        return result.get('data').get('address')


async def get_disk_space_for_hosting(session):
    result = await fetch('/info/disk_space_for_hosting/', session)
    if result.get('status') == 'success':
        return result.get('data').get('disk_space_for_hosting')


async def get_host_ip(session):
    result = await fetch('/info/host_ip/', session)
    if result.get('status') == 'success':
        return result.get('data').get('host_ip')


async def get_balance(session):
    result = await fetch('/user/balance/', session)
    if result.get('status') == 'success':
        return result.get('data').get('balance')


async def get_space_used(session):
    result = await fetch('/info/space_used/', session)
    if result.get('status') == 'success':
        return result.get('data').get('space_used')


async def get_box_gir(session):
    result = await fetch('/info/boxes_dir/', session)
    if result.get('status') == 'success':
        return result.get('data').get('boxes_dir')


async def get_token_price(session):
    # ToDo: implement
    return 0.1


async def create_account(role, session):
    async with session.post(
            f'{settings.daemon_address}/user/create/',
            json={
                "role": role
            }
    ) as result:
        if result.status == 201:
            return True
        else:
            data = await result.json()
            msg = data.get('message')
            error_handler(f'Account creation failed.\n{msg}')
            return False


async def generate_address(password, session):
    async with session.post(
            f'{settings.daemon_address}/user/create/',
            json={
                "password": password
            }
    ) as result:
        if result.status == 201:
            data = await result.json()
            return data.get('address')
        else:
            data = await result.json()
            msg = data.get('message')
            error_handler(f'Generating address failed.\n{msg}')
            return False


async def request_mmr(key, session):
    async with session.post(
            f'{settings.daemon_address}/request_mmr/',
            json={
                "key": key
            }
    ) as result:
        data = await result.json()
        if data.get('status') == 'success':
            return data.get('balance')
        else:
            data = await result.json()
            msg = data.get('message')
            error_handler(f'Requesting MMR failed.\n'
                          f'{msg}\n'
                          f'Please ensure if the key was entered correctly.')
            return None


async def import_account(filename, session):
    async with session.post(
            f'{settings.daemon_address}/user/import/',
            json={
                "filename": filename
            }
    ) as result:
        if result.status != 200:
            data = await result.json()
            msg = data.get('message')
            error_handler(msg)
            return False
    return True


async def export_account(filename, session):
    async with session.post(
            f'{settings.daemon_address}/user/export/',
            json={
                "filename": filename
            }
    ) as result:
        if result.status != 200:
            data = await result.json()
            msg = data.get('message')
            error_handler(msg)
            return False
    return True


async def set_disk_space_for_hosting(disk_space, session):
    await session.post(f'{settings.daemon_address}/disk_space/', json={"disk_space": disk_space})


async def change_box_dir(box_dir, session):
    await session.post(f'{settings.daemon_address}/change_box_dir/', json={"box_dir": box_dir})
