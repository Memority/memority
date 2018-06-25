#!/usr/bin/env python3

import sys
import requests
from w3base import W3Base
from web3.contract import ConciseContract

class Migrate(W3Base):

    migrate_version = 1000

    @staticmethod
    def get_clients():
        r = requests.get(url='https://api.memority.io/api/app/clients/get')
        addrs = []
        for addr in r.json()['addresses']:
            addrs.append(addr['address'])

        return addrs

    def import_hosts(self, host_list, contract_instance):
        for host in host_list:
            self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])

            result = contract_instance.importHost(
                host, host_list[host]['ip'], host_list[host]['power'], host_list[host]['active'],
                transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})

            self.log('import host ' + host)
            print(result)

    def import_clients(self, client_contract, contract_instance):
        for client in client_contract:
            self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])

            if client_contract[client]:
                result = contract_instance.importClient(
                    client, client_contract[client],
                    transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})

                self.log('import client ' + client)

    def import_transactions(self, transactions, contract_instance):
        for client in transactions:
            for transaction in transactions[client]:
                self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])

                from_addr = transaction['from'] if transaction['from'] else '0x0000000000000000000000000000000000000000'
                to_addr = transaction['to'] if transaction['to'] else '0x0000000000000000000000000000000000000000'
                result = contract_instance.importTransaction(
                    transaction['id'], client, from_addr, to_addr, transaction['file'],
                    transaction['date'], transaction['value'],
                    transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})

            self.log('import '+str(len(transactions[client]))+' transactions')

    def get_instance(self, new_contract_address=''):
        if not new_contract_address:
            new_contract = self.make_bin_and_deploy('MemoDB', self.migrate_version)
            new_contract_instance = self.w3.eth.contract(
                new_contract['source']['abi'],
                new_contract['address'],
                ContractFactoryClass=ConciseContract
            )
        else:
            new_contract_source = self.compile('MemoDB.v' + str(self.migrate_version))

            new_contract_instance = self.w3.eth.contract(
                new_contract_source['abi'],
                new_contract_address,
                ContractFactoryClass=ConciseContract
            )

        return new_contract_instance

    def transfer_db(self, version, new_contract_address=''):
        self.migrate_version = version
        self.prepare_contract('MemoDB')

        # get old data
        hostList = {}
        clientContract = {}
        transactions = {}

        clients = self.get_clients()
        hosts = self.contract_instance.getHosts()
        for host in hosts:
            hostInfo = self.contract_instance.hostInfo(host)
            hostList[host] = {
                'hostAddress': hostInfo[0],
                'ip': hostInfo[1],
                'power': hostInfo[2],
                'active': hostInfo[3]
            }

        for client in clients:
            clientContract[client] = self.contract_instance.clientContract(client)
            count = self.contract_instance.transactionsCount(client)
            transactions[client] = []
            if count:
                for i in range(count):
                    transaction_id = self.contract_instance.transactionsId(client, i)
                    transaction = self.contract_instance.transactions(transaction_id)
                    transactions[client].append({
                        'from': transaction[0],
                        'to': transaction[1],
                        'file': transaction[2],
                        'date': transaction[3],
                        'value': transaction[4],
                        'id': transaction_id
                    })

        # ### prepare new contract
        new_contract_instance = self.get_instance(new_contract_address)

        # ### insert new data
        self.import_hosts(hostList, new_contract_instance)
        self.import_clients(clientContract, new_contract_instance)
        self.import_transactions(transactions, new_contract_instance)
        #todo: setActualDb(...)


migration_version = 1000
previous_version = 1000
contract_address = ''     # deploy new if empty

migration = Migrate(previous_version)
migration.transfer_db(migration_version, contract_address)
