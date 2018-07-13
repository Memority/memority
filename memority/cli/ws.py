import aiohttp
import json
from aiohttp import ClientConnectorError

from .utils import Exit, get_url

__all__ = ['send_ws']


async def handle_info(data, _):
    print(data.get('message'))


async def handle_success(data, _):
    if data.get('details') == 'uploaded':
        raise Exit('File successfully uploaded!')

    elif data.get('details') == 'downloaded':
        raise Exit('File successfully downloaded!')


async def handle_error(data, _):
    raise Exit(f'Error: {data.get("message")}')


async def handle_action(data, ws):
    if data.get('details') == 'ask_for_password':
        raise Exit('Unlock account first.')

    elif data.get('details') == 'tokens_to_deposit':
        print(f'Enter the token amount for deposit.\n'
              f'Price for 2 weeks for this file: '
              f'{data.get("data").get("price_per_hour")*24*14:.18f}')

        result = input('>> ')

        await ws.send_json({'status': 'success', 'result': result})

    else:
        print(data)


async def process_ws_message(msg, ws):
    data = json.loads(msg.data)
    status = data.get('status')
    data_handler = {
        "info": handle_info,
        "success": handle_success,
        "error": handle_error,
        "action_needed": handle_action,
    }.get(status)

    if data_handler:
        await data_handler(data, ws)


async def send_ws(data_to_send: dict, port: int):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(get_url('/ws/', port=port)) as ws:
                await ws.send_json(data_to_send)
                async for msg in ws:
                    await process_ws_message(msg, ws)

        except ClientConnectorError:
            raise Exit('No response from the daemon')
