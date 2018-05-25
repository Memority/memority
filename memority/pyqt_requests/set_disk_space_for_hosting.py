from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class SetDiskSpaceForHostingRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, disk_space):
        super().__init__(
            '/disk_space/',
            {"disk_space": disk_space}
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
