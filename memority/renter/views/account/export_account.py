from settings import settings


async def export_account(data):
    filename = data.get('filename')
    settings.export_account(filename)
    return 'ok'
