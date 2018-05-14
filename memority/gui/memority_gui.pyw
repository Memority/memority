import sys

import contextlib
import requests
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from quamash import QApplication

from settings import settings

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class DaemonInterface:

    def __init__(self, daemon_address):
        self.daemon_address = daemon_address

    def get_user_address(self):
        resp = requests.get(f'{self.daemon_address}/info/address/').json()
        if resp.get('status') == 'success':
            return resp.get('data').get('address')

    def get_user_balance(self):
        resp = requests.get(f'{self.daemon_address}/user/balance/').json()
        if resp.get('status') == 'success':
            return resp.get('data').get('balance') or 0
        return 0

    def get_user_role(self):
        resp = requests.get(f'{self.daemon_address}/user/role/').json()
        if resp.get('status') == 'success':
            return resp.get('data').get('role')

    def ping_daemon(self):
        with contextlib.suppress(requests.exceptions.ConnectionError):
            resp = requests.get(f'{self.daemon_address}/ping/')
            return resp.status_code == 200

    def is_first_run(self):
        resp = requests.get(f'{self.daemon_address}/check_first_run/').json()
        if resp.get('status') == 'success':
            return resp.get('result')

    def unlock_account(self, password):
        resp = requests.post(f'{self.daemon_address}/unlock/', json={"password": password})
        return resp.status_code == 200

    def get_disk_space_for_hosting(self):
        resp = requests.get(f'{self.daemon_address}/info/disk_space_for_hosting/').json()
        if resp.get('status') == 'success':
            return resp.get('data').get('disk_space_for_hosting')

    def get_box_dir(self):
        resp = requests.get(f'{self.daemon_address}/info/boxes_dir/').json()
        if resp.get('status') == 'success':
            return resp.get('data').get('boxes_dir')

    def generate_address(self, password):
        resp = requests.post(
            f'{self.daemon_address}/user/create/',
            json={
                "password": password
            }
        )
        data = resp.json()
        if resp.status_code == 201:
            return True, data.get('address')
        else:
            msg = data.get('message')
            return False, f'Generating address failed.\n{msg}'

    def request_mmr(self, key):
        resp = requests.post(
            f'{self.daemon_address}/request_mmr/',
            json={
                "key": key
            }
        )
        data = resp.json()
        if data.get('status') == 'success':
            return True, data.get('balance')
        else:
            msg = data.get('message')
            return False, f'Requesting MMR failed.\n{msg}\nPlease ensure if the key was entered correctly.'

    def create_account(self, role):
        resp = requests.post(
            f'{self.daemon_address}/user/create/',
            json={
                "role": role
            }
        )
        if resp.status_code == 201:
            return True, ...
        else:
            data = resp.json()
            msg = data.get('message')
            return False, f'Account creation failed.\n{msg}'


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon_interface = DaemonInterface(settings.daemon_address)
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
        self.refresh()

    def setup_ui(self):
        self.ui.closeEvent = self.closeEvent
        self.ui.buy_mmr_btn.hide()
        self.ui.transfer_mmr_btn.hide()
        self.ui.transaction_history_lbl.hide()
        self.ui.transaction_history_table.hide()
        self.ui.refresh_btn.clicked.connect(self.refresh)
        self.ui.copy_address_btn.clicked.connect(self.copy_address_to_clipboard)
        self.ui.create_account_btn.clicked.connect(self.create_account)

    def log(self, msg):
        self.ui.log_widget.appendPlainText(msg)
        self.ui.log_widget.moveCursor(QTextCursor.End)

    @pyqtSlot()
    def refresh(self):
        """
        get role
        enable-disable tabs
        """
        role = self.daemon_interface.get_user_role()
        self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.My_files))
        self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.Hosting_statistics))
        self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.Settings))
        if role in ['client', 'both']:
            self.ui.tabWidget.addTab(self.ui.My_files, "My files")
        if role in ['hoster', 'both']:
            self.ui.tabWidget.addTab(self.ui.Hosting_statistics, "Hosting statistics")
        self.ui.tabWidget.addTab(self.ui.Settings, "Settings")
        self.refresh_wallet_tab()
        self.refresh_files_tab()
        self.refresh_hosting_tab()
        self.refresh_settings_tab()

    def refresh_wallet_tab(self):
        # region Address
        address = self.daemon_interface.get_user_address()
        if address:
            self.ui.copy_address_btn.setEnabled(True)
        else:
            address = 'Please go to "Settings" - "Create account"'
        # endregion
        # region Balance
        balance = self.daemon_interface.get_user_balance()
        # endregion
        self.ui.address_display.setText(address)
        self.ui.balance_display.setText(f'{balance} MMR')

    def refresh_files_tab(self):
        ...

    def refresh_hosting_tab(self):
        ...

    def refresh_settings_tab(self):
        role = self.daemon_interface.get_user_role()
        disk_space_for_hosting = self.daemon_interface.get_disk_space_for_hosting()
        box_dir = self.daemon_interface.get_box_dir()

        self.ui.disk_space_input.setValue(disk_space_for_hosting)
        self.ui.directory_input.setText(box_dir)
        for element in [
            self.ui.create_account_btn,
            self.ui.import_account_btn,
            self.ui.export_account_btn,
            self.ui.become_hoster_btn,
            self.ui.hosting_settings_widget
        ]:
            element.hide()
        self.ui.import_account_btn.show()
        if role:
            self.ui.export_account_btn.show()
            if role in ['hoster', 'both']:
                self.ui.hosting_settings_widget.show()
            elif role == 'client':
                self.ui.become_hoster_btn.show()
        else:
            self.ui.create_account_btn.show()

    @pyqtSlot()
    def copy_address_to_clipboard(self):
        self.ui.address_display: QLineEdit
        QApplication.clipboard().setText(self.ui.address_display.text())

    @pyqtSlot()
    def create_account(self):
        # region Generate address
        generate_address_dialog: QDialog = uic.loadUi(settings.ui_generate_address)
        if not generate_address_dialog.exec_():
            return
        password1 = generate_address_dialog.password1.text()
        password2 = generate_address_dialog.password2.text()

        if password1 != password2:
            QMessageBox.critical(None, 'Error', 'Passwords don`t match!')
            return

        self.log(f'Generating address...')
        ok, result = self.daemon_interface.generate_address(password=password1)
        if not ok:
            QMessageBox.critical(None, 'Error', result)
            return
        self.log(f'Your address: {result}')
        self.refresh()
        # endregion

        # region Request MMR
        add_key_dialog: QDialog = uic.loadUi(settings.ui_add_key)
        if not add_key_dialog.exec_():
            return
        self.log('Please wait while we’ll send you MMR tokens for testing, it may take a few minutes. '
                 'Do not close the application.')
        ok, result = self.daemon_interface.request_mmr(key=add_key_dialog.key_input.text())
        if not ok:
            QMessageBox.critical(None, 'Error', result)
            return
        self.log(f'Tokens received. Your balance: {result} MMR')
        # endregion

        # region Create account
        create_account_dialog: QDialog = uic.loadUi(settings.ui_create_account)
        if not create_account_dialog.exec_():
            return
        role = {
            0: 'client',
            1: 'host',
            2: 'both'
        }.get(create_account_dialog.role_input.currentIndex())

        self.log(f'Creating account for role "{role}"...\n'
                 f'This can take up to 60 seconds, as transaction is being written in blockchain.')
        if role in ['client', 'both']:
            self.log('Creating client account. When finished, the "My Files" tab appears.')
            ok, result = self.daemon_interface.create_account(role='client')
            if not ok:
                QMessageBox.critical(None, 'Error', result)
                return
            self.log('Client account successfully created!')
            self.refresh()
        if role in ['host', 'both']:
            self.log('Creating hoster account. When finished, the "Hosting statistics" tab appears.')
            ok, result = self.daemon_interface.create_account(role='host')
            if not ok:
                QMessageBox.critical(None, 'Error', result)
                return
            self.log('Hoster account successfully created!')
            self.refresh()
        # endregion

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
            daemon_running = self.daemon_interface.ping_daemon()
            if daemon_running:
                return
            _ok = QMessageBox().question(
                None,
                "Is the Memority Core running?",
                f'Can`t connect to Memority Core. Is it running?\n'
                f'Please launch Memority Core before Memority UI.\n'
                f'If you have already started Memority Core, wait a few seconds and try again.',
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok
            )
            if _ok != QMessageBox.Ok:
                self.shutdown()
                sys.exit()

    def unlock_account(self):
        if not self.daemon_interface.is_first_run():
            while True:
                password, ok = QInputDialog.getText(None, "Password", "Password:", QLineEdit.Password)
                if not ok:
                    self.shutdown()
                    sys.exit()
                if self.daemon_interface.unlock_account(password):
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
