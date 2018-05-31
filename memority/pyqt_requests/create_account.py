from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class CreateAccountRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, role):
        super().__init__(
            '/user/create/',
            {"role": role}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, ''
            )
        else:
            msg = data.get('message')
            self.finished.emit(
                False, f'Account creation failed.\n{msg}'
            )
