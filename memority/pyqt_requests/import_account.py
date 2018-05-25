from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class ImportAccountRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, filename):
        super().__init__(
            '/user/import/',
            {"filename": filename}
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
