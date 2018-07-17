from settings import settings


async def import_account(filename, password):
    settings.import_account(filename, password)
    return 'ok'
