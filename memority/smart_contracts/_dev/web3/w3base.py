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
import bitcoin as b
from ethereum import utils
import binascii
import codecs

class W3Base:

    contract_path = '../../contracts/'
    cfg = ''
    passwords = ''
    __location__ = ''
    contract_interface = ''
    contract_instance = ''
    contract_address = ''
    w3 = ''
    version = ''

    def __init__(self, version=''):
        self.version = version
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        with open(os.path.join(self.__location__, 'config.yml'), 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

        with open(os.path.join(self.__location__, 'passwords.yml'), 'r') as ymlfile:
            self.passwords = yaml.load(ymlfile)

        self.log('contract version: ' + str(self.version))

    @staticmethod
    def error(msg):
        print('error: ' + msg)
        sys.exit()

    @staticmethod
    def log(msg):
        print('[=] ' + msg)

    def get_conf(self, key):
        if self.version:
            if 'version_' + str(self.version) not in self.cfg:
                self.error('version section not found')

            if key not in self.cfg['version_' + str(self.version)]:
                self.error('version config not found')

            return self.cfg['version_' + str(self.version)][key]
        else:
            return self.cfg[key]

    def prepare_contract(self, contract_name, contract_address=''):

        addresses = {
            'Token': self.get_conf('token_address'),
            'MemoDB': self.get_conf('db_address'),
            'Client': self.get_conf('client'),
            'Utils': self.get_conf('utils')
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
        return format(self.w3.eth.getTransactionReceipt(tx)) + "\n\n" + format(self.w3.eth.getTransaction(tx))

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
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
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
            'Utils': [],
        }

        full_name = contract_name + ('.v' + str(contract_version) if contract_version else '')
        source = self.compile_source(full_name, contract_name)
        self.prepare_contract(contract_name)
        result = self.deploy(source, deploy_options[contract_name])
        result['source'] = source

        return result

    def compile(self, name):
        bin_name = name+'.v'+str(self.version)+'.bin' if self.version else name+'.bin'
        contract_bin_file = os.path.join(self.__location__, self.contract_path + 'bin/' + bin_name)

        if not os.path.exists(contract_bin_file):
            contract_bin_file = os.path.join(self.__location__, self.contract_path + 'bin/' + name+'.v'+str(self.migrate_version)+'.bin')

        with open(contract_bin_file, 'rb') as f:
            self.contract_interface = pickle.load(f)

        return self.contract_interface

    def get_contract(self):
        if self.contract_address == '':
            self.log('no contract_address')
            return
            # self.error('no contract_address')

        self.contract_instance = self.w3.eth.contract(
            self.contract_interface['abi'],
            self.contract_address,
            ContractFactoryClass=ConciseContract
        )

    def to_mmr_wei(self, amount):
        return int(amount) * 10 ** self.cfg['token_decimals']

    def from_mmr_wei(self, amount):
        return int(amount) / 10 ** self.cfg['token_decimals']

    def set_token_db(self, address):
        self.prepare_contract('Token')
        #self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
        result = self.contract_instance.setDbAddress(address, transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
        return format(result)

    def set_db_token_address(self, address):
        self.prepare_contract('MemoDB')
        result = self.contract_instance.changeToken(address, transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
        return format(result)

    def set_client_contract(self, address):
        self.prepare_contract('MemoDB')
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
        result = self.contract_instance.newClient(address, transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
        return format(result)

    def change_client_token_address(self, address):
        self.prepare_contract('Client')
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
        result = self.contract_instance.changeTokenAddress(address, transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
        return format(result)

    def refill_contract(self, amount):
        self.prepare_contract('Token')
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
        result = self.w3.eth.sendTransaction({
            'to':  self.contract_address,
            'from':  self.cfg['token_owner'],
            'value':  self.w3.toWei(amount, 'ether'),
            'gas': self.cfg['gas']
        })
        return format(result)

    def sign_message(self, message):
        self.prepare_contract('Token')
        sha = self.w3.sha3(text=message)
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
        signature = self.w3.eth.sign(self.cfg['token_owner'], hexstr=sha)

        return format(signature)

    def check_sign_py(self, message, signature):
        # todo: find correct way
        print("owner address: " + self.cfg['token_owner'])
        self.prepare_contract('Utils')
        msghash = self.w3.sha3(text=message)[2:]
        print("w.sha3: " + str(msghash))

        prefix = '\x19Ethereum Signed Message:\n32'
        msg2 = prefix + msghash
        msghash2 = self.w3.sha3(text=msg2)[2:]
        print("hash2: "+ str(msghash2))

        msghash = bytearray.fromhex(self.w3.sha3(text=message)[2:])
        result = self.contract_instance.keccak(msghash)
        print("keckack: "+ str(result))

        r = int(signature[0:66], 16)
        s = int('0x'+signature[66:130], 16)
        v = int('0x'+signature[130:132], 16)
        if not v == 27 and not v == 28:
            v += 27

        # msghash = codecs.decode(msghash, "hex")
        msghash = result.encode().hex()
        # print(msghash)

        recovered_addr = b.ecdsa_raw_recover(msghash, (v, r, s))
        pub = b.encode_pubkey(recovered_addr, 'bin')
        address = binascii.hexlify(utils.sha3(pub[1:]))[24:64]
        return format(address.decode('utf-8'))

    def check_sign(self, message, signature):
        print("owner address: " + self.cfg['token_owner'])
        self.prepare_contract('Utils')

        msghash = self.w3.sha3(text=message)[2:]
        r = bytearray.fromhex(signature[2:66])
        s = bytearray.fromhex(signature[66:130])
        v = int('0x'+signature[130:132], 16)

        if not v == 27 and not v == 28:
            v += 27

        msghash = bytearray.fromhex(msghash)
        result = self.contract_instance.verify(r, s, v, msghash)
        return format(result)

    def status(self):
        self.prepare_contract('Token')

        result = 'Token address: ' + format(self.contract_address) + "\n" + \
                 'Token balance: ' + format(self.w3.fromWei(self.w3.eth.getBalance(self.contract_address), 'ether')) + " ETH\n" + \
                 'Total supply: ' + format(self.contract_instance.totalSupply()) + \
                 'MMR; For Sale: ' + format(self.contract_instance.tokenForSale()) + " MMR\n" + \
                 'Token price: ' + format(self.contract_instance.tokenPrice()) + " Eth\n" + \
                 'DB address: ' + format(self.contract_instance.dbAddress()) + "\n" + \
                 'Version: ' + format(self.contract_instance.version()) + "\n"

        client_balance = format(self.contract_instance.balanceOf(self.cfg['client_address']))

        self.prepare_contract('MemoDB')

        result += 'Total hosts: ' + format(len(self.contract_instance.getHosts())) + "\n" + \
            'Total clients: ' + format(self.contract_instance.clientsCount()) + "\n" + \
            'Client contract: ' + format(self.contract_instance.clientContract(self.cfg['token_owner'])) + "\n"

        self.prepare_contract('Client')
        result += 'Total client files: ' + format(len(self.contract_instance.getFiles())) + "\n" + \
            'Client balance: ' + format(self.from_mmr_wei(client_balance)) + ' MMR' + " \n"

        # # debug
        # self.prepare_contract('MemoDB')
        # result += ('msg_sender: ' + format(self.contract_instance.msg_sender())) + " \n"
        # result += ('param_sender: ' + format(self.contract_instance.param_sender())) + " \n"

        return result




