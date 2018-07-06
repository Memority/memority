import os

from .base import send_ws


async def upload_file(args):
    path = args.path
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    data = {
        "command": "upload",
        "kwargs": {
            "path": path
        }
    }
    return await send_ws(data, port=args.memority_core_port)
