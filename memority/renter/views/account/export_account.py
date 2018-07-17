from settings import settings


async def export_account(filename):
    settings.export_account(filename)
    return 'ok'
