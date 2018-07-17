from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class ChangeBoxDirRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, path):
        super().__init__(
            '/host/storage/set_path/',
            {"path": path}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, ''
            )
        else:
            msg = data.get('message')
            self.finished.emit(
                False, msg
            )
