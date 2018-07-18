from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class GetUserBalanceRequest(AbstractPostRequest):
    finished = pyqtSignal(float)

    def __init__(self):
        super().__init__('/user/balance/', {})

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('result')
            )
