from ..ws import send_ws


async def update_client_contract(args):
    data = {
        "command": "update_client_contract",
    }
    return await send_ws(data, port=args.memority_core_port)
