from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class MinerStatusRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__(
            '/miner_request/',
            {}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, str(data.get('request_status'))
            )
        else:
            self.finished.emit(
                False, data.get('message')
            )
