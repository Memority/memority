from settings import settings
from smart_contracts import create_w3


async def get_sync_status():
    if not settings.SYNC_STARTED:
        data = {
            "syncing": True,
            "percent": -1
        }
    else:
        w3 = create_w3()
        status = w3.eth.syncing
        if status:
            current = status.get('currentBlock')
            highest = status.get('highestBlock')
            percent = int(current / highest * 100)
            data = {
                "syncing": True,
                "percent": percent
            }
        else:
            data = {
                "syncing": False,
                "percent": 100
            }
    return data
