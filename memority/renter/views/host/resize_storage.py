from settings import settings


async def resize_storage(disk_space):
    # ToDo: check if not lower than space used
    settings.disk_space_for_hosting = float(disk_space)
    return 'ok'
