from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetSyncStatusRequest(AbstractGetRequest):
    finished = pyqtSignal(bool, int)

    def __init__(self):
        super().__init__('/checks/sync_status/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            result = data.get('data').get('result')
            self.finished.emit(
                result.get('syncing'),
                result.get('percent')
            )
