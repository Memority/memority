import requests

from ..utils import get_url


async def get_transactions(args):
    r = requests.post(get_url('/user/transactions/', port=args.memority_core_port), json={})
    data = r.json()
    if data.get('status') != 'success':
        print(f'Error: {data.get("message")}')
        return
    transactions = data.get('result')
    row = "{:<43}{sep}{:<43}{sep}{:<25}{sep}{:<20}{sep}{:<32}"
    print(row.format('From', 'To', 'Value, MMR', 'Date', 'Comment', sep='| '))
    print(row.format('-' * 43, '-' * 43, '-' * 25, '-' * 20, '-' * 32, sep='+-'))
    for tx in transactions:
        print(
            row.format(
                tx['from'] or '-',
                tx['to'] or '-',
                f"{tx['value']:02.18f}",
                tx['date'],
                tx['comment'],
                sep='| '
            )
        )


l = [
    {
        'comment': 'enroll',
        'date': '2018-07-04T11:18:05',
        'from': None,
        'to': '0x4D03FC8F5147205C07BE57b24B2DF6F2E605EDC0',
        'value': 50.0
    },
    {
        'comment': '938be0a8e822eeb240c8ad42950e36c1',
        'date': '2018-07-04T11:28:35',
        'from': '0x4D03FC8F5147205C07BE57b24B2DF6F2E605EDC0',
        'to': None,
        'value': 1.5097824e-08
    }
]
