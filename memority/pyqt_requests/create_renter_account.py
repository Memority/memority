from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class CreateRenterAccountRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__(
            '/account/create/',
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
                False, f'Account creation failed.\n{msg}'
            )
