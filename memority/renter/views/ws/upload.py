import aiohttp
import asyncio
import logging
from aiohttp import web, ClientConnectorError

from bugtracking import raven_client
from models import RenterFile, Host
from settings import settings
from smart_contracts import client_contract, token_contract, memo_db_contract


# ToDo: upload if metadata in contract but not in hosts

class FileUploader:
    class UploadingError(Exception):
        ...

    def __init__(self, websocket: web.WebSocketResponse, path: str) -> None:
        self._websocket = websocket
        self.logger = logging.getLogger('memority')
        self.file_path = path
        self.file: RenterFile = None
        self.hosters = set()

    async def perform_uploading(self):
        try:
            client_contract.reload()
            token_contract.reload()
            memo_db_contract.reload()
            await self.notify_user(f'Started file uploading | path: {self.file_path}')
            await self.open_file()
            self.check_file_not_already_uploaded()
            self.prepare_file()
            await self.notify_user('Search for hosters...')
            await self.find_hosters()
            await self.create_file_metadata()
            self.file.status = RenterFile.METADATA_CREATED
            self.file.save()
            await self.create_deposit()
            self.file.status = RenterFile.DEPOSIT_CREATED
            self.file.save()
            await self.notify_user(f'Uploading file to {len(self.hosters)} hosters...')
            await self.upload_to_hosters()
            # ToDo: check if uploaded to hosters
            self.file.status = RenterFile.UPLOADED
            self.file.save()
            await self.notify_user(
                f'Finished file uploading '
                f'| path: {self.file_path} '
                f'| hash: {self.file.hash}'
            )
            return {
                "status": "success",
                "details": "uploaded",
                "result": {
                    "file": await self.file.to_json()
                }
            }
        except self.UploadingError as err:
            return self.error(str(err))

    async def open_file(self):
        self.file = await RenterFile.open(self.file_path)

    def check_file_not_already_uploaded(self):
        if self.file.hash in client_contract.get_files():
            raise self.UploadingError(
                f'The file is already uploaded '
                f'| path: {self.file_path} '
                f'| hash: {self.file.hash}'
            )

    def prepare_file(self):
        self.file.prepare_to_uploading()

    async def find_hosters(self):
        hosters = set(Host.get_n(n=10))
        if not hosters:
            raise self.UploadingError(f'No hosters available')
        hosts_error = set()
        while True:
            done, _ = await asyncio.wait(
                [
                    asyncio.ensure_future(
                        self.get_hoster_free_space(
                            hoster=hoster
                        )
                    )
                    for hoster in hosters
                ]
            )
            for task in done:
                hoster, space = task.result()
                if space >= self.file.size:
                    self.hosters.add(hoster)
                else:
                    hosts_error.add(hoster)
            if len(self.hosters) >= 10:
                break
            else:
                hosters = set(Host.get_n(n=10 - len(self.hosters))) \
                    .difference(self.hosters) \
                    .difference(hosts_error)
                if not hosters:
                    if self.hosters:
                        break
                    else:
                        self.file.delete()
                        raise self.UploadingError("No hosters available!")

    async def create_file_metadata(self):
        file_metadata_for_contract = {
            "file_name": self.file.name,
            "file_size": self.file.size,
            "file_hash": self.file.hash,
            "hosts": [hoster.address for hoster in self.hosters]
        }
        try:
            await self.notify_user(
                f'Sending file metadata to contract '
                f'| file: {self.file.hash}...\n'
                f'This can take some time, as transaction is being written in blockchain.'
            )
            await client_contract.new_file(**file_metadata_for_contract)
        except Exception as err:
            raven_client.captureException()
            self.file.delete()
            raise self.UploadingError(
                f'Saving data to contract failed '
                f'| file: {self.file.hash} '
                f'| message: {err.__class__.__name__} {str(err)}'
            )

    async def create_deposit(self):
        if not await token_contract.get_deposit(file_hash=self.file.hash):
            token_balance = token_contract.get_mmr_balance()
            tokens_to_deposit = await self.ask_user_for_deposit_size()
            if tokens_to_deposit == -1:
                raise self.UploadingError('Cancelled.')
            if not tokens_to_deposit:
                raise self.UploadingError('Invalid value')

            tokens_to_deposit = float(tokens_to_deposit)
            if tokens_to_deposit > token_balance:
                raise self.UploadingError(
                    f'Deposit can not be bigger than your balance.'
                    f'| mmr balance: {token_balance}'
                )

            await self.notify_user(
                f'Creating deposit for file {self.file.hash}, value: {tokens_to_deposit} MMR... '
                f'This can take some time, as transaction is being written in blockchain.'
            )

            await client_contract.make_deposit(value=tokens_to_deposit, file_hash=self.file.hash)

            if not await token_contract.get_deposit(file_hash=self.file.hash):
                raise self.UploadingError(
                    f'Failed deposit creation '
                    f'| file: {self.file.hash}'
                )

            await self.notify_user('Deposit successfully created.')

    async def upload_to_hosters(self):
        data = {
            "file_hash": self.file.hash,
            "owner_key": settings.public_key,
            "signature": self.file.signature,
            "client_address": settings.address,
            "size": self.file.size,
            "hosts": [hoster.address for hoster in self.hosters]
        }

        hosts_success = set()
        hosts_error = set()

        done, _ = await asyncio.wait(
            [
                asyncio.ensure_future(
                    self.upload_to_hoster(
                        hoster=hoster,
                        data=data,
                    )
                )
                for hoster in self.hosters
            ]
        )
        for task in done:
            hoster, ok = task.result()
            if ok:
                hosts_success.add(hoster)
            else:
                hosts_error.add(hoster)

        await self.notify_user(f'Successfully uploaded to {len(hosts_success)} hosters')

    async def ask_user_for_deposit_size(self):
        await self._websocket.send_json({
            "status": "action_needed",
            "details": 'tokens_to_deposit',
            "result": {
                "size": self.file.size,
                "price_per_hour": token_contract.wmmr_to_mmr(
                    token_contract.tokens_per_byte_hour * self.file.size * 10
                )
            }
        })
        try:
            resp = await self._websocket.receive_json()
            return resp.get('result')
        except TypeError:
            return None

    async def get_hoster_free_space(self, hoster: Host):
        self.logger.info(
            f'Get free space from hoster '
            f'| {hoster}'
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://{hoster.ip}/free-space/', timeout=1) as resp:
                    if resp.status == 200:
                        resp_data = await resp.json()
                        return hoster, resp_data.get('data').get('result')
                    else:
                        return hoster, 0
        except (ClientConnectorError, asyncio.TimeoutError) as err:
            self.logger.warning(
                f'Host is not accessible '
                f'| {hoster} '
                f'| {err}'
            )
            return hoster, 0

    async def upload_to_hoster(self, hoster, data):
        try:
            async with aiohttp.ClientSession() as session:
                self.logger.info(
                    f'Uploading file metadata to hoster... '
                    f'| file: {self.file.hash} '
                    f'| hoster ip: {hoster.ip}'
                )
                async with session.post(
                        f'http://{hoster.ip}/files/',
                        json=data
                ) as resp1:
                    resp_data: dict = await resp1.json()
                    if resp_data.get('status') != 'success':
                        return hoster, False

                self.logger.info(
                    f'Uploading file body to hoster... '
                    f'| file: {self.file.hash} '
                    f'| hoster ip: {hoster.ip}'
                )
                async with session.put(
                        f'http://{hoster.ip}/files/{self.file.hash}/',
                        data=self.file.get_filelike(),
                        timeout=None
                ) as resp2:
                    resp_data: dict = await resp2.json()
                    if resp_data.get('status') != 'success':
                        return hoster, False

            await self.notify_user(
                f'Uploaded to {hoster.address} '
                f'| file: {self.file.hash} '
                f'| hoster ip: {hoster.ip}'
            )
            return hoster, True

        except (ClientConnectorError, asyncio.TimeoutError) as err:
            self.logger.warning(
                f'Uploading to hoster failed '
                f'| file: {self.file.hash} '
                f'| hoster: {hoster.address} '
                f'| message: {err.__class__.__name__} {str(err)}'
            )
            return hoster, False

    async def notify_user(self, msg):
        self.logger.info(msg)
        await self._websocket.send_json({
            "status": "info",
            "message": msg
        })

    def error(self, msg):
        self.logger.warning(msg)
        return {
            "status": "error",
            "message": msg
        }
