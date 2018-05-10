import sys

import contextlib
import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QMessageBox, QInputDialog, QLineEdit, QStyleFactory
from quamash import QApplication

from settings import settings

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.ws_client = QWebSocket()
        # self.ws_client.error.connect(self.error)
        # self.ws_client.open(QUrl(f'ws://{settings.daemon_address}'))
        # self.ws_client.textMessageReceived.connect(self.on_msg_received)
        self.ui: QWidget = uic.loadUi(settings.ui_main_window)
        self.setup_ui()
        self.ensure_daemon_running()
        self.unlock_account()
        sg = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        self.move(
            int((sg.width() - widget.width()) / 4),
            int((sg.height() - widget.height()) / 3)
        )
        self.ui.show()

    def setup_ui(self):
        self.ui.closeEvent = self.closeEvent
        self.ui.buy_mmr_btn.hide()
        self.ui.transfer_mmr_btn.hide()
        self.ui.refresh_btn.clicked.connect(self.refresh)
        self.ui.copy_address_btn.clicked.connect(self.copy_address_to_clipboard)
        self.refresh()

    def refresh_wallet_tab(self):
        # region Address
        resp = requests.get(f'{settings.daemon_address}/info/address/').json()
        if resp.get('status') == 'success':
            address = resp.get('data').get('address')
            self.ui.copy_address_btn.setEnabled(True)
        else:
            address = 'Please go to "Settings" - "Generate address"'
        # endregion
        # region Balance
        resp = requests.get(f'{settings.daemon_address}/user/balance/').json()
        if resp.get('status') == 'success':
            balance = resp.get('data').get('balance') or 0
        else:
            balance = 0
        # endregion
        token_price = 0.1  # ToDo: get exchange rate
        self.ui.address_display.setText(address)
        self.ui.balance_display.setText(f'{balance} MMR')
        self.ui.mmr_price_display.setText(f'1 MMR = {token_price} USD')

    def refresh_files_tab(self):
        ...

    def refresh_hosting_tab(self):
        ...

    def refresh_settings_tab(self):
        ...

    @pyqtSlot()
    def refresh(self):
        """
        get role
        enable-disable tabs
        """
        self.refresh_wallet_tab()
        self.refresh_files_tab()
        self.refresh_hosting_tab()
        self.refresh_settings_tab()

    @pyqtSlot()
    def copy_address_to_clipboard(self):
        self.ui.address_display: QLineEdit
        QApplication.clipboard().setText(self.ui.address_display.text())

    def closeEvent(self, event):
        reply = QMessageBox().question(
            self,
            "Are you sure to quit?",
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.shutdown()
            event.accept()
        else:
            event.ignore()

    def ensure_daemon_running(self):
        while True:
            with contextlib.suppress(requests.exceptions.ConnectionError):
                resp = requests.get(f'{settings.daemon_address}/ping/')
                if resp.status_code == 200:
                    return
            _ok = QMessageBox().question(
                None,
                "Is the Memority Core running?",
                f'Can`t connect to Memority Core. Is it running?\n'
                f'Please launch Memority Core before Memority UI.',
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok
            )
            if _ok != QMessageBox.Ok:
                self.shutdown()
                sys.exit()

    def unlock_account(self):
        if not requests.get(f'{settings.daemon_address}/check_first_run/').json().get('result'):
            while True:
                password, ok = QInputDialog.getText(None, "Password", "Password:", QLineEdit.Password)
                if not ok:
                    self.shutdown()
                    sys.exit()
                if requests.post(
                        f'{settings.daemon_address}/unlock/',
                        json={"password": password}
                ).status_code == 200:
                    break
                else:
                    QMessageBox().critical(None, 'Error!', 'Invalid password!')
                    continue

    def shutdown(self):
        ...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = MainWindow()
    sys.exit(app.exec_())
