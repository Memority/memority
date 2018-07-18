from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class GetUserFilesRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str, list)

    def __init__(self):
        super().__init__('/files/list/', {})

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True,
                '',
                data.get('result')
            )
        else:
            self.finished.emit(
                False,
                data.get('message'),
                []
            )
