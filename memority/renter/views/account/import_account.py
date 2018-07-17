from settings import settings


async def import_account(data):
    filename = data.get('filename')
    password = data.get('password')
    settings.import_account(filename, password)
    return 'ok'
