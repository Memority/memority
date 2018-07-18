from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class GetFileMetadataRequest(AbstractPostRequest):
    finished = pyqtSignal(dict)

    def __init__(self, file_hash):
        super().__init__(f'/files/info/', {"file_hash": file_hash})

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('result')
            )
