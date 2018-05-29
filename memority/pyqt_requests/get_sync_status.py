from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetSyncStatusRequest(AbstractGetRequest):
    finished = pyqtSignal(bool, int)

    def __init__(self):
        super().__init__('/sync_status/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('data').get('syncing'),
                data.get('data').get('percent')
            )
