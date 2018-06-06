#!/usr/bin/env python3

import sys

from w3base import W3Base

version_to_use = 1000

ether = W3Base(version_to_use)

if len(sys.argv) < 2:
    ether.error('usage: python3 run.py cmd')

if str(sys.argv[1]) == 'status':
    result = ether.status()
    print(result)

elif str(sys.argv[1]) == 'tx':
    result = ether.tx_detail(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'set_token_db':
    result = ether.set_token_db('0x27C823b254C74989201cEc2A9db6eBbBf169eED0')
    print(result)

elif str(sys.argv[1]) == 'set_client_contract':
    result = ether.set_client_contract('0xBf5a83294Ca896Ef70F666C4826f46317Df33233')
    print(result)

