from models import RenterFile


async def file_info(file_hash):
    file = RenterFile.objects.get(hash=file_hash)
    return await file.to_json()
