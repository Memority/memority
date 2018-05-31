from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetFileMetadataRequest(AbstractGetRequest):
    finished = pyqtSignal(dict)

    def __init__(self, file_hash):
        super().__init__(f'/files/{file_hash}/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('data')
            )
