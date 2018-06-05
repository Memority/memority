#!/usr/bin/env python3


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import pickle
import yaml

from time import sleep
from solc import compile_source
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract


class W3Base:

    contract_path = '../../contracts/'
    cfg = ''
    __location__ = ''
    contract_interface = ''
    contract_instance = ''
    contract_address = ''
    w3 = ''

    def __init__(self):
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        with open(os.path.join(self.__location__, 'config.yml'), 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

    @staticmethod
    def error(msg):
        print('error: ' + msg)
        sys.exit()

    @staticmethod
    def log(msg):
        print('[=] ' + msg)

    def prepare_contract(self, contract_name, contract_address=''):

        addresses = {
            'Token': self.cfg['token_address'],
            'MemoDB': self.cfg['db_address'],
            'Client': self.cfg['client']
        }

        if not contract_address:
            contract_address = addresses[contract_name]

        self.contract_address = contract_address

        self.w3 = Web3(HTTPProvider(self.cfg['w3_url']))
        self.compile(contract_name)
        self.get_contract()

    def compile_source(self, sol_name, contract_name):
        contract_source_code = open(self.contract_path + sol_name+'.sol','r').read()
        compiled_sol = compile_source(contract_source_code)
        contract_interface = compiled_sol['<stdin>:'+contract_name]

        with open(self.contract_path + 'bin/'+sol_name+'.bin', 'wb') as f:
            pickle.dump(contract_interface, f, pickle.HIGHEST_PROTOCOL)

        return contract_interface

    def tx_detail(self, tx):
        self.prepare_contract('Token')
        return format(self.w3.eth.getTransactionReceipt(tx))

    def get_address_by_tx(self, tx):
        tx_receipt = self.w3.eth.getTransactionReceipt(tx)
        if tx_receipt and 'contractAddress' in tx_receipt:
            print('')
            return tx_receipt['contractAddress']
        else:
            print('.', end='', flush=True)
            sleep(1)
            return self.get_address_by_tx(tx)

    def deploy(self, contract_interface, args):
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.cfg['token_owner_password'])
        contract = self.w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
        tx_hash = contract.deploy(transaction={'from': self.cfg['token_owner'], 'gas': self.cfg['gas']}, args=args)
        self.log('tx hash: ' + tx_hash)
        address = self.get_address_by_tx(tx_hash)
        self.log('address: ' + address)

        return {
            'tx': tx_hash,
            'address': address,
            'source': ''
        }

    def make_bin_and_deploy(self, contract_name, contract_version=''):
        deploy_options = {
            'MemoDB': [self.cfg['version_' + str(self.migrate_version)]['token_address']],
            'Token': [1500000000, 1, 'Memority Token', 'MMR'],
            'Client': [self.cfg['version_' + str(self.migrate_version)]['token_address']],
        }

        full_name = contract_name + ('.v' + str(contract_version) if contract_version else '')
        source = self.compile_source(full_name, contract_name)
        self.prepare_contract(contract_name)
        result = self.deploy(source, deploy_options[contract_name])
        result['source'] = source

        return result

    def compile(self, name):
        contract_bin_file = os.path.join(self.__location__, self.contract_path + 'bin/'+name+'.bin')
        with open(contract_bin_file, 'rb') as f:
            self.contract_interface = pickle.load(f)

        return self.contract_interface

    def get_contract(self):
        if self.contract_address == '':
            self.error('no contract_address')

        self.contract_instance = self.w3.eth.contract(
            self.contract_interface['abi'],
            self.contract_address,
            ContractFactoryClass=ConciseContract
        )

    def to_mmr_wei(self, amount):
        return int(amount) * 10 ** self.cfg['token_decimals']

    def from_mmr_wei(self, amount):
        return int(amount) / 10 ** self.cfg['token_decimals']

    # def enroll(self, to, amount):
    #     amount = self.to_mmr_wei(amount)
    #     self.w3.personal.unlockAccount(self.cfg['token_owner'], self.cfg['token_owner_password'])
    #     result = self.contract_instance.enroll(to, amount, transact={'from': self.cfg['token_owner'], 'gas': self.cfg['gas']})
    #     return format(result)

    def set_token_db(self, address):
        self.prepare_contract('Token')
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.cfg['token_owner_password'])
        result = self.contract_instance.setDbAddress(address, transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
        return format(result)

    def status(self):
        self.prepare_contract('Token')

        result = 'Total supply: ' + format(self.contract_instance.totalSupply()) + \
                 ' MMR; For Sale: ' + format(self.contract_instance.tokenForSale()) + " MMR\n" + \
                 'Token price: ' + format(self.contract_instance.tokenPrice()) + " Eth\n" + \
                 'DB address: ' + format(self.contract_instance.dbAddress()) + "\n"

        client_balance = format(self.contract_instance.balanceOf(self.cfg['client_address']))

        self.prepare_contract('MemoDB')

        result += 'Total hosts: ' + format(len(self.contract_instance.getHosts())) + "\n" + \
            'Client contract: ' + format(self.contract_instance.clientContract(self.cfg['client_address'])) + "\n"

        self.prepare_contract('Client')
        result += 'Total client files: ' + format(len(self.contract_instance.getFiles())) + "\n" + \
            'Client balance: ' + format(self.from_mmr_wei(client_balance)) + ' MMR'

        return result




