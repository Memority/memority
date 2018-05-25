from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class ChangeBoxDirRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, box_dir):
        super().__init__(
            '/change_box_dir/',
            {"box_dir": box_dir}
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
