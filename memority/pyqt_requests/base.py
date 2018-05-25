import json
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from abc import ABC, abstractmethod
from abc import ABCMeta

from settings import settings

__all__ = ['AbstractGetRequest', 'AbstractPostRequest']


class AbstractRequestMeta(type(QObject), ABCMeta):
    pass


class AbstractGetRequest(QObject, ABC, metaclass=AbstractRequestMeta):

    # noinspection PyArgumentList, PyUnresolvedReferences
    def __init__(self, rel_url: str):
        print(f'init {self.__class__.__name__}')
        QObject.__init__(self, parent=None)
        ABC.__init__(self)
        self.url = QUrl(f'http://{settings.daemon_address}{rel_url}')
        self.req = QNetworkRequest(self.url)
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.process_response)

    def send(self):
        print(f'send {self.__class__.__name__}')
        self.nam.get(self.req)

    def process_response(self, response: QNetworkReply):
        print(f'done {self.__class__.__name__}')
        data: QByteArray = response.readAll()
        resp_data = json.loads(data.data().decode('utf-8'))
        return self.process_response_data(resp_data)

    @property
    @abstractmethod
    def finished(self):
        pass

    @abstractmethod
    def process_response_data(self, data: dict):
        pass


class AbstractPostRequest(QObject, ABC, metaclass=AbstractRequestMeta):

    # noinspection PyArgumentList, PyUnresolvedReferences
    def __init__(self, rel_url: str, post_data: dict):
        print(f'init {self.__class__.__name__}')
        super().__init__(parent=None)
        self.url = QUrl(f'http://{settings.daemon_address}{rel_url}')

        self.post_data = QByteArray()
        self.post_data.append(json.dumps(post_data))

        self.req = QNetworkRequest(self.url)
        self.req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.process_response)

    def send(self):
        print(f'send {self.__class__.__name__}')
        self.nam.post(self.req, self.post_data)

    def process_response(self, response: QNetworkReply):
        print(f'done {self.__class__.__name__}')
        data: QByteArray = response.readAll()
        resp_data = json.loads(data.data().decode('utf-8'))
        return self.process_response_data(resp_data)

    @abstractmethod
    def process_response_data(self, data: dict):
        pass

    @property
    @abstractmethod
    def finished(self):
        pass
