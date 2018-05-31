from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetSpaceUsedRequest(AbstractGetRequest):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__('/info/space_used/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('data').get('space_used')
            )
