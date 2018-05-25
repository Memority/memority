from PyQt5.QtCore import pyqtSignal
from PyQt5.QtNetwork import QNetworkReply

from .base import AbstractGetRequest


class PingRequest(AbstractGetRequest):
    finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__('/ping/')

    def process_response(self, response: QNetworkReply):
        print(f'done {self.__class__.__name__}')
        if response.error() == QNetworkReply.NoError:
            self.finished.emit(True)
        else:
            print(response.errorString())
            self.finished.emit(False)

    def process_response_data(self, data: dict):
        pass
