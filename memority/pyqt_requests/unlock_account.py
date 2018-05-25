import json
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

from settings import settings


class UnlockRequest(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, *, parent=None, password):
        print('init UnlockRequest')
        super().__init__(parent)
        self.url = QUrl(f'http://{settings.daemon_address}/unlock/')

        self.post_data = QByteArray()
        self.post_data.append(json.dumps({"password": password}))

        self.req = QNetworkRequest(self.url)
        self.req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.process_response)

    def send(self):
        print('send UnlockRequest')
        self.nam.post(self.req, self.post_data)

    def process_response(self, response: QNetworkReply):
        print('done UnlockRequest')
        data: QByteArray = response.readAll()
        resp_data = json.loads(data.data().decode('utf-8'))
        if resp_data.get('status') == 'success':
            self.finished.emit(True)
        else:
            self.finished.emit(False)
