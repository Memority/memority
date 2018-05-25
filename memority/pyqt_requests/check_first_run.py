from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class CheckFirstRunRequest(AbstractGetRequest):
    finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__('/check_first_run/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(data.get('result'))
