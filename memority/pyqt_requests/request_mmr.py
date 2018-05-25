from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class RequestMMRRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, key):
        super().__init__(
            '/request_mmr/',
            {"key": key}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, data.get('balance')
            )
        else:
            msg = data.get('message')
            self.finished.emit(
                False, f'Requesting MMR failed.\n{msg}\nPlease ensure if the key was entered correctly.'
            )
