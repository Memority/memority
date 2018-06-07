from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetUserFilesRequest(AbstractGetRequest):
    finished = pyqtSignal(bool, str, list)

    def __init__(self):
        super().__init__('/files/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True,
                '',
                data.get('data').get('files')
            )
        else:
            self.finished.emit(
                False,
                data.get('message'),
                []
            )
