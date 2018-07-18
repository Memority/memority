from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class GetUserAddressRequest(AbstractPostRequest):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__('/user/address/', {})

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('result')
            )
        else:
            self.finished.emit('')
