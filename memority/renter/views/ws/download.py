import aiohttp
import logging
import os
from aiohttp import web

from models import RenterFile
from utils import DecryptionError


class FileDownloader:
    class DownloadingError(Exception):
        ...

    def __init__(self, websocket: web.WebSocketResponse, file_hash: str, destination: str) -> None:
        self._websocket = websocket
        self.logger = logging.getLogger('memority')
        self.file_hash = file_hash
        self.destination = destination
        self.file = None

    async def perform_downloading(self):
        try:
            await self.notify_user(f'Started downloading file {self.file_hash} to {self.destination}')
            self.find_file()
            await self.download_and_decrypt_file()
            await self.save_file()
            return {
                "status": "success",
                "details": "downloaded",
                "result": {
                    "file": {
                        "name": os.path.join(self.destination, self.file.name)
                    }
                }
            }
        except self.DownloadingError as err:
            return self.error(str(err))

    def find_file(self):
        RenterFile.refresh_from_contract()
        try:
            self.file = RenterFile.find(hash_=self.file_hash)
        except RenterFile.NotFound:
            raise self.DownloadingError(
                f'File not found '
                f'| {self.file_hash}'
            )

    async def download_and_decrypt_file(self):
        for hoster in self.file.hosters:
            await self.notify_user(
                f'Trying to download file... '
                f'| file: {self.file_hash} '
                f'| hoster: {hoster.address}'
            )
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'http://{hoster.ip}/files/{self.file_hash}/') as response:
                        assert response.status == 200
                        # ToDo: handle error message
                        file_body = await response.read()
            except Exception as err:
                self.logger.warning(
                    f'Downloading from hoster failed '
                    f'| file: {self.file_hash} '
                    f'| hoster: {hoster.address} '
                    f'| message: {err.__class__.__name__} {str(err)}'
                )
                continue

            self.file.load_body(file_body)
            self.logger.info(
                f'Decrypting file '
                f'| file: {self.file_hash} '
                f'| hoster: {hoster.address}'
            )
            try:
                self.file.decrypt()
            except DecryptionError:
                self.logger.error(
                    f'Failed file decrypting '
                    f'| file: {self.file_hash} '
                    f'| hoster: {hoster.address}'
                )
                continue
            await self.notify_user(
                f'File successfully downloaded and decrypted '
                f'| file: {self.file_hash} '
                f'| hoster: {hoster.address}'
            )
            break
        else:
            raise self.DownloadingError(
                f"Downloading from each of {len(self.file.hosters)} hosters failed! "
                f"| file: {self.file_hash} "
                f"| hosters: {', '.join([h.address for h in self.file.hosters])}"
            )

    async def save_file(self):
        try:
            await self.file.save_to_fs(destination=self.destination)
        except FileExistsError:
            # ToDo: overwrite existing?
            raise self.DownloadingError("The file already exists! Please specify a different path.")
        except PermissionError as err:
            self.logger.warning(str(err))
            raise self.DownloadingError(str(err))

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
