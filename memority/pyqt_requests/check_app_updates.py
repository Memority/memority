from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class CheckAppUpdatesRequest(AbstractGetRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__('/app_updates/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('data').get('update_available'),
                data.get('data').get('download_url')
            )
