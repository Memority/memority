#!/usr/bin/env python3

import sys

from w3base import W3Base

version_to_use = 1020

ether = W3Base(version_to_use)

if len(sys.argv) < 2:
    ether.error('usage: python3 run.py cmd')

if str(sys.argv[1]) == 'status':
    result = ether.status()
    print(result)

elif str(sys.argv[1]) == 'tx':
    result = ether.tx_detail(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'refill_contract':
    result = ether.refill_contract(1000000)
    print(result)

elif str(sys.argv[1]) == 'refill_address':
    result = ether.refill_address(str(sys.argv[2]), sys.argv[3])
    print(result)

elif str(sys.argv[1]) == 'set_token_db':
    result = ether.set_token_db('0x822DA535db237A07BBB37f3Ff7303b2Acc6550C7')
    print(result)

elif str(sys.argv[1]) == 'set_db_token_address':
    result = ether.set_db_token_address('0xC62685E2Ff940FE0a73052Bd5D876d7D2c9d70b4')
    print(result)

elif str(sys.argv[1]) == 'set_client_contract':
    result = ether.set_client_contract('0xBf5a83294Ca896Ef70F666C4826f46317Df33233')
    print(result)

elif str(sys.argv[1]) == 'change_client_token_address':
    result = ether.change_client_token_address('0xBf5a83294Ca896Ef70F666C4826f46317Df33233')
    print(result)

elif str(sys.argv[1]) == 'sign_message':
    result = ether.sign_message(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'check_sign':
    # result = ether.check_sign(str(sys.argv[2]), str(sys.argv[3]))
    result = ether.check_sign(str(sys.argv[2]), str(sys.argv[3]))
    print(result)

elif str(sys.argv[1]) == 'node_info':
    result = ether.get_enode()
    print(result)

elif str(sys.argv[1]) == 'vote_for_host':
    result = ether.vote_for_host(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'token_balance':
    result = ether.token_balance(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'get_block':
    result = ether.get_block(int(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'get_last_block':
    result = ether.get_last_block()
    print(result)

elif str(sys.argv[1]) == 'get_transactions':
    result = ether.get_transactions(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'get_deposits':
    result = ether.get_deposits(str(sys.argv[2]), str(sys.argv[3]))
    print(result)

elif str(sys.argv[1]) == 'get_client_contract':
    result = ether.get_client_contract(str(sys.argv[2]))
    print(result)

elif str(sys.argv[1]) == 'get_files':
    address = ''
    if len(sys.argv) == 3:
        address = str(sys.argv[2])
        print('addr: ' +address)

    result = ether.get_client_files(address)
    print(result)


