from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class ProlongDepositForFileRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, file_hash, value):
        super().__init__(
            f'/files/prolong_deposit/',
            {
                "value": value,
                "file_hash": file_hash
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
                False, f'Deposit creation failed.\n{msg}'
            )
