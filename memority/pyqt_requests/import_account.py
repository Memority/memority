from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class ImportAccountRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, filename, password):
        super().__init__(
            '/account/import/',
            {
                "filename": filename,
                "password": password
            }
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, ''
            )
        else:
            msg = data.get('message')
            self.finished.emit(
                False, f'Importing account failed.\n{msg}'
            )
