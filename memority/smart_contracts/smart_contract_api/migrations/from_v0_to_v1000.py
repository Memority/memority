from settings import settings
from smart_contracts import ClientContract, client_contract, unlock_account, wait_for_transaction_completion


class Migration0to1000:
    def __init__(self) -> None:
        self.old_contract = client_contract.contract
        self.new_contract = ClientContract()

    async def apply(self):
        print('Reading data from old contract...')
        client_files = self.get_client_files()
        print(f'Found {len(client_files)} file(s).')

        print('Deploying new smart contract...')
        address = await self.new_contract.deploy(overwrite_addr_in_settings=False)
        version = self.new_contract.current_version
        print('Done.')

        print('Importing files...')
        await self.import_files(client_files)

        settings.client_contract_address = address
        settings.client_contract_version = version
        print('Done.')

    def get_client_files(self):
        client_files = []

        files = self.old_contract.getFiles()

        for file in files:
            file_hosts = self.old_contract.getFileHosts(file)
            file_detail = self.old_contract.fileList(file)
            client_files.append({
                'hash': file,
                'name': file_detail[0],
                'size': file_detail[2],
                'developer': file_detail[4],
                'timestamp': file_detail[3],
                'hosts': file_hosts,
            })
        return client_files

    async def import_files(self, client_files):
        await unlock_account()
        for file in client_files:
            print(f'Importing file {file["hash"]}...')
            tx_hash = self.new_contract.contract.importFile(
                file['hash'],
                file['name'],
                file['size'],
                file['timestamp'],
                file['developer'],
                file['hosts'],
                transact={'from': settings.address, 'gas': 4_000_000}
            )
            await wait_for_transaction_completion(tx_hash)
