#!/usr/bin/env python3

import sys
import requests
from w3base import W3Base
from web3.contract import ConciseContract
from web3.exceptions import BadFunctionCallOutput

class Migrate(W3Base):

    migrate_version = 1000

    def import_balance(self, holders_balances, contract_instance):
        for client in holders_balances:
            self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])

            result = contract_instance.importBalance(
                client, holders_balances[client]['balance'],
                transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})

            self.log('import balance ' + client + ' = ' + str(holders_balances[client]['balance']))

    def import_total(self, data, contract_instance):
        self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])

        result = contract_instance.importTotal(
            data['totalSupply'], data['tokenForSale'], data['holdersToken'],
            transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})

    def import_deposits(self, client_files, contract_instance):
        for client in client_files:
            for file in client_files[client]:
                deposit = self.contract_instance.deposits(client, file)
                print('deposit for ' + file + ' = ' + str(deposit))
                self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
                result = contract_instance.importDeposits(
                    client, file, deposit,
                    transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
                print(result)

    def import_payouts(self, client_file_hosts, contract_instance):
        for file in client_file_hosts:
            for host in client_file_hosts[file]:
                time = self.contract_instance.payouts(file, host)
                print('payout for ' + file + ' ['+host+'] > ' + str(time))
                self.w3.personal.unlockAccount(self.cfg['token_owner'], self.passwords['token_owner_password'])
                result = contract_instance.importPayouts(
                    file, host, time,
                    transact={'from':  self.cfg['token_owner'], 'gas': self.cfg['gas']})
                print(result)

    def get_instance(self, new_contract_address=''):
        if not new_contract_address:
            new_contract = self.make_bin_and_deploy('Token', self.migrate_version)
            new_contract_instance = self.w3.eth.contract(
                new_contract['source']['abi'],
                new_contract['address'],
                ContractFactoryClass=ConciseContract
            )
        else:
            new_contract_source = self.compile('Token.v' + str(self.migrate_version))

            new_contract_instance = self.w3.eth.contract(
                new_contract_source['abi'],
                new_contract_address,
                ContractFactoryClass=ConciseContract
            )

        return new_contract_instance

    def transfer_db(self, version, new_contract_address=''):
        self.migrate_version = version
        self.prepare_contract('Token')

        # get old data
        holdersBalances = {}
        clientFiles = {}
        clientFileHosts = {}
        totalData = {
            'totalSupply': self.contract_instance.totalSupply(),
            'tokenForSale': self.contract_instance.tokenForSale(),
            'holdersToken': self.contract_instance.holdersToken()
        }

        x = 0
        while True:
            try:
                holder = self.contract_instance.holdersList(x)
            except BadFunctionCallOutput:
                break
            else:
                holdersBalances[holder] = {
                    'balance': self.contract_instance.balanceOf(holder)
                }
                x = x+1

        for holder in holdersBalances:
            self.prepare_contract('MemoDB')
            client_address = self.contract_instance.clientContract(holder)

            self.prepare_contract('Client', client_address)
            files = self.contract_instance.getFiles()

            if client_address:
                clientFiles[client_address] = files
                for file in files:
                    file_hosts = self.contract_instance.getFileHosts(file)
                    clientFileHosts[file] = file_hosts

        self.prepare_contract('Token')

        # ### prepare new contract
        new_contract_instance = self.get_instance(new_contract_address)

        # ### insert new data
        self.import_total(totalData, new_contract_instance)
        self.import_balance(holdersBalances, new_contract_instance)
        self.import_deposits(clientFiles, new_contract_instance)
        self.import_payouts(clientFileHosts, new_contract_instance)


migration_version = 1000
previous_version = ''
contract_address = '0x124D1f206646Fe9C26693981459471b893be286c'     # deploy new if empty

migration = Migrate(previous_version)
migration.transfer_db(migration_version, contract_address)
