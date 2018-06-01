import json
import platform
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

from bugtracking import raven_client


class GetLatestVersionRequest(QObject):
    finished = pyqtSignal(str, str)

    # noinspection PyArgumentList, PyUnresolvedReferences
    def __init__(self):
        print(f'init {self.__class__.__name__}')
        QObject.__init__(self, parent=None)
        self.url = QUrl('https://api.memority.io/api/app/version')
        self.req = QNetworkRequest(self.url)
        self.req.setSslConfiguration(QSslConfiguration.defaultConfiguration())
        self.req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.process_response)

    def send(self):
        print(f'send {self.__class__.__name__}')
        self.nam.get(self.req)

    def process_response(self, response: QNetworkReply):
        print(f'done {self.__class__.__name__}')
        data: QByteArray = response.readAll()
        try:
            resp_data = json.loads(data.data().decode('utf-8'))
            self.finished.emit(
                resp_data.get('latest'),
                resp_data.get(
                    {
                        'Linux': 'download_linux',
                        'Windows': 'download_windows',
                        'Darwin': 'download_macos'
                    }.get(platform.system())
                )
            )
        except json.decoder.JSONDecodeError as err:
            raven_client.captureException(extra={
                "error": response.errorString()
            })
            print(response.errorString())
            print(err)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    print(QSslSocket.supportsSsl())
    r = GetLatestVersionRequest()
    r.finished.connect(lambda *args, **kwargs: print(f'{args} | {kwargs}'))
    r.send()
    sys.exit(app.exec_())
