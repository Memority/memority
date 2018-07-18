from PyQt5.QtCore import pyqtSignal

from .base import AbstractPostRequest


class GenerateAddressRequest(AbstractPostRequest):
    finished = pyqtSignal(bool, str)

    def __init__(self, password):
        super().__init__(
            '/account/generate_address/',
            {"password": password}
        )

    def process_response_data(self, data: dict):
        if data.get('status') == 'success':
            self.finished.emit(
                True, data.get('result')
            )
        else:
            msg = data.get('message')
            self.finished.emit(
                False, f'Generating address failed.\n{msg}'
            )
