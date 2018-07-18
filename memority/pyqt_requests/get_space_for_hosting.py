from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetDiskSpaceForHostingRequest(AbstractGetRequest):
    finished = pyqtSignal(float)

    def __init__(self):
        super().__init__('/info/disk_space_for_hosting/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('result').get('disk_space_for_hosting')
            )
