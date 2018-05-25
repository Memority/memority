from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

from settings import settings


class PingRequest(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, parent=None):
        print('init PingRequest')
        super().__init__(parent)
        self.url = QUrl(f'http://{settings.daemon_address}/ping/')
        self.req = QNetworkRequest(self.url)
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.process_response)

    def send(self):
        print('send PingRequest')
        self.nam.get(self.req)

    def process_response(self, response: QNetworkReply):
        print('done PingRequest')
        if response.error() == QNetworkReply.NoError:
            self.finished.emit(True)
        else:
            print(response.errorString())
            self.finished.emit(False)
