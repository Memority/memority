from PyQt5.QtCore import pyqtSignal

from .base import AbstractGetRequest


class GetUserIPRequest(AbstractGetRequest):
    finished = pyqtSignal(str)

    def __init__(self):
        super().__init__('/info/host_ip/')

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                data.get('result').get('host_ip')
            )
