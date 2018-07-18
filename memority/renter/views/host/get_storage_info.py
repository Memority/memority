from models import HosterFile
from settings import settings


async def get_storage_info():
    return {
        "total": settings.disk_space_for_hosting * (1024 ** 3),
        "used": HosterFile.get_total_size()
    }
