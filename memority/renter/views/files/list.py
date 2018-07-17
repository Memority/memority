from models import RenterFile
from utils import check_first_run


async def list_files():
    if check_first_run():
        return []

    RenterFile.refresh_from_contract()

    return await RenterFile.list()
