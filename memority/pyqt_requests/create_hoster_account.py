from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class CreateHosterAccountRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__(
            '/host/start/',
            {}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, ''
            )
        else:
            msg = data.get('message')
            self.finished.emit(
                False, f'Adding to host list failed.\n{msg}'
            )
