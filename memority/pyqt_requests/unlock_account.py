from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class UnlockRequest(AbstractPostRequest):
    finished = pyqtSignal(bool)

    def __init__(self, password):
        super().__init__(
            '/unlock/',
            {"password": password}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(True)
        else:
            self.finished.emit(False)
