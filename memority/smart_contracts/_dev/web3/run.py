#!/usr/bin/env python3

import sys

from w3base import W3Base

ether = W3Base()

if len(sys.argv) < 2:
    ether.error('usage: python3 run.py cmd')

if str(sys.argv[1]) == 'status':
    result = ether.status()
    print(result)

elif str(sys.argv[1]) == 'tx':
    result = ether.tx_detail(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'set_token_db':
    result = ether.set_token_db('0x853A9E1017bC9D9117ddDA4Ec9f4087fc51a9C1D')
    print(result)

