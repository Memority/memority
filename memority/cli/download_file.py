from .base import send_ws


async def download_file(args):
    data = {
        "command": "download",
        "kwargs": {
            "file_hash": args.hash,
            "destination": args.destination
        }
    }

    return await send_ws(data, port=args.memority_core_port)
