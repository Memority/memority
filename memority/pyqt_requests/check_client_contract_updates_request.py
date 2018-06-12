from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class CheckClientContractUpdatesRequest(AbstractGetRequest):
    finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__('/contract_updates/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(data.get('data').get('result'))
