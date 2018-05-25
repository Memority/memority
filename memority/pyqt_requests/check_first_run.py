import json
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

from settings import settings


class CheckFirstRunRequest(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, parent=None):
        print('init CheckFirstRunRequest')
        super().__init__(parent)
        self.url = QUrl(f'http://{settings.daemon_address}/check_first_run/')
        self.req = QNetworkRequest(self.url)
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.process_response)

    def send(self):
        print('send CheckFirstRunRequest')
        self.nam.get(self.req)

    def process_response(self, response: QNetworkReply):
        print('done CheckFirstRunRequest')
        data: QByteArray = response.readAll()
        resp_data = json.loads(data.data().decode('utf-8'))
        if resp_data.get('status') == 'success':
            self.finished.emit(resp_data.get('result'))
