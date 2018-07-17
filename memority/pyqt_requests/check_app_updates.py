from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class CheckAppUpdatesRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__('/checks/app_updates/', {})

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            result = data.get('data')
            self.finished.emit(
                result.get('update_available'),
                result.get('download_url')
            )
