from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class CheckClientContractUpdatesRequest(AbstractPostRequest):
    finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__('/checks/contract_updates/', {})

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(data.get('result'))
