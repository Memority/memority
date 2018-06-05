#!/usr/bin/env python3

import sys
import requests
from w3base import W3Base
from web3.contract import ConciseContract
from web3.exceptions import BadFunctionCallOutput


class Migrate(W3Base):

    migrate_version = 1000

    def import_files(self, client_files, contract_instance):
        for file in client_files:
            self.w3.personal.unlockAccount(self.cfg['client_address'], self.cfg['client_pass'])
            result = contract_instance.importFile(
                file['hash'],
                file['name'],
                file['size'],
                file['timestamp'],
                file['developer'],
                file['hosts'],
                transact={'from':  self.cfg['client_address'], 'gas': self.cfg['gas']})
            self.log('import file: ' + file['name'])
            print(result)

    def get_instance(self, new_contract_address=''):
        if not new_contract_address:
            new_contract = self.make_bin_and_deploy('Client', self.migrate_version)
            new_contract_instance = self.w3.eth.contract(
                new_contract['source']['abi'],
                new_contract['address'],
                ContractFactoryClass=ConciseContract
            )
        else:
            new_contract_source = self.compile('Client.v' + str(self.migrate_version))

            new_contract_instance = self.w3.eth.contract(
                new_contract_source['abi'],
                new_contract_address,
                ContractFactoryClass=ConciseContract
            )

        return new_contract_instance

    def transfer_db(self, version, new_contract_address=''):
        self.migrate_version = version

        # get old data
        clientFiles = []

        self.prepare_contract('Client')
        files = self.contract_instance.getFiles()

        for file in files:
            file_hosts = self.contract_instance.getFileHosts(file)
            file_detail = self.contract_instance.fileList(file)
            clientFiles.append({
                'hash': file,
                'name': file_detail[0],         # self.contract_instance.getFileName(file),
                'size': file_detail[2],         # self.contract_instance.getFileSize(file),
                'developer': file_detail[4],    # self.contract_instance.getFileDeveloper(file),
                'timestamp': file_detail[3],
                'hosts': file_hosts,
            })

        ### prepare new contract
        new_contract_instance = self.get_instance(new_contract_address)

        ### insert new data
        self.import_files(clientFiles, new_contract_instance)


migration_version = 1000
contract_address = ''     # deploy new if empty

migration = Migrate()
migration.transfer_db(migration_version, contract_address)
