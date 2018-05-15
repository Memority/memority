import sys

import contextlib
import json
import os
import requests
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta
from functools import partial

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

    def get_files(self):
        resp = requests.get(f'{self.daemon_address}/files/').json()
        return resp.get('data').get('files')

    def export_account(self, filename):
        resp = requests.post(
            f'{self.daemon_address}/user/export/',
            json={
                "filename": filename
            }
        )
        if resp.status_code != 200:
            data = resp.json()
            msg = data.get('message')
            return False, msg
        return True, ...

    def import_account(self, filename):
        resp = requests.post(
            f'{self.daemon_address}/user/import/',
            json={
                "filename": filename
            }
        )
        if resp.status_code != 200:
            data = resp.json()
            msg = data.get('message')
            return False, msg
        return True, ...


# noinspection PyArgumentList
class MainWindow(QMainWindow):

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon_interface = DaemonInterface(f'http://{settings.daemon_address}')
        self.ui: QWidget = uic.loadUi(settings.ui_main_window)
        self.setup_ui()
        self.ensure_daemon_running()
        self.unlock_account()
        self.ws_client = QWebSocket()
        self.ws_client.error.connect(self.ws_error)
        self.ws_client.textMessageReceived.connect(self.ws_on_msg_received)
        self.ws_client.open(QUrl(f'ws://{settings.daemon_address}'))
        sg = QDesktopWidget().screenGeometry()
        widget = self.ui.geometry()
        self.ui.move(
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
        self.ui.import_account_btn.clicked.connect(self.import_account)
        self.ui.export_account_btn.clicked.connect(self.export_account)
        self.ui.become_hoster_btn.clicked.connect(self.become_a_hoster)
        self.ui.directory_change_btn.clicked.connect(self.change_directory)
        self.ui.settings_apply_btn.clicked.connect(self.apply_settings)
        self.ui.settings_reset_btn.clicked.connect(self.reset_settings)
        self.ui.disk_space_input.valueChanged.connect(self.enable_hosting_settings_controls)
        self.ui.directory_input.textChanged.connect(self.enable_hosting_settings_controls)
        self.ui.upload_file_btn.clicked.connect(self.upload_file)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def log(self, msg):
        self.ui.log_widget.appendPlainText(msg)
        self.ui.log_widget.moveCursor(QTextCursor.End)
        self.ui.log_widget.repaint()

    def error(self, msg: str):
        self.log(msg)
        msg = msg.replace('\n', '<br/>')
        dialog: QDialog = uic.loadUi(settings.ui_error_msg)
        dialog.msg.setText(
            f'<html><body>{msg}</html></body>'
        )
        dialog.adjustSize()
        dialog.exec_()

    @staticmethod
    def notify(msg):
        QMessageBox.information(None, 'Info', msg)

    def ws_send(self, data: dict):
        self.ws_client.sendTextMessage(json.dumps(data))

    @pyqtSlot(QAbstractSocket.SocketError)
    def ws_error(self, error_code):
        self.log(f'Error {error_code}: {self.ws_client.errorString()}')
        self.error(self.ws_client.errorString())

    @pyqtSlot(str)
    def ws_on_msg_received(self, payload: str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as err:
            self.error(str(err))
            return
        status = data.get('status')
        if status == 'info':
            self.log(data.get('message'))
        elif status == 'action_needed':
            if data.get('details') == 'tokens_to_deposit':
                self.choose_tokens_for_deposit(**data.get('data', {}))
        elif status == 'success':
            if data.get('details') == 'uploaded':
                self.notify('File successfully uploaded!')
            elif data.get('details') == 'downloaded':
                self.notify('File successfully downloaded!')
            self.refresh_files_tab()
        elif status == 'error':
            self.error(data.get('message'))

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
        self.ui.file_list_scrollarea_layout: QVBoxLayout
        self.ui.file_list_spacer: QSpacerItem
        files = self.daemon_interface.get_files()
        if not files:
            return
        self.clear_layout(self.ui.file_list_scrollarea_layout)
        for file in files:
            file_list_item = uic.loadUi(settings.ui_file_list_item)
            file_list_item.uploaded_on_display.setText(file.get('timestamp'))
            file_list_item.name_display.setText(file.get('name'))
            file_list_item.hash_display.setText(file.get('hash'))
            file_list_item.deposit_end_display.setText(file.get('deposit_ends_on'))
            file_list_item.download_btn.clicked.connect(partial(self.download_file, file.get('hash')))
            self.ui.file_list_scrollarea_layout.addWidget(file_list_item)
        self.ui.file_list_scrollarea_layout.addItem(QSpacerItem(QSizePolicy.Expanding, QSizePolicy.Expanding, 0, 0))

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

        self.ui.settings_apply_btn.setDisabled(True)
        self.ui.settings_reset_btn.setDisabled(True)

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
            self.error('Passwords don`t match!')
            return

        self.log(f'Generating address...')
        ok, result = self.daemon_interface.generate_address(password=password1)
        if not ok:
            self.error(result)
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
            self.error(result)
            return
        self.refresh()
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
                self.error(result)
                return
            self.refresh()
            self.log('Client account successfully created!')
        if role in ['host', 'both']:
            self.log('Creating hoster account. When finished, the "Hosting statistics" tab appears.')
            ok, result = self.daemon_interface.create_account(role='host')
            if not ok:
                self.error(result)
                return
            self.refresh()
            self.log('Hoster account successfully created!')
        # endregion

    @pyqtSlot()
    def import_account(self):
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Select account file",
            os.path.join(os.getenv('HOME', None) or os.getenv('HOMEPATH', None), 'memority_account.bin'),
            "*.bin"
        )
        if filename:
            self.log('Importing account...')
            ok, result = self.daemon_interface.import_account(filename)
            if ok:
                self.log(f'Successfully imported {filename}')
                self.unlock_account()
            else:
                self.error(result)
        self.refresh()

    @pyqtSlot()
    def export_account(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Select a location to save your account file.",
            os.path.join(os.getenv('HOME', None) or os.getenv('HOMEPATH', None), 'memority_account.bin'),
            "*.bin"
        )
        if filename:
            self.log('Exporting account...')
            ok, result = self.daemon_interface.export_account(filename)
            if ok:
                self.log(f'Exported to {filename}')
            else:
                self.error(result)

    @pyqtSlot()
    def become_a_hoster(self):
        self.log('Adding your address and IP to contract...\n'
                 'This can take up to 60 seconds, as transaction is being written in blockchain.\n'
                 'When finished, the "Hosting statistics" tab appears.')
        ok, result = self.daemon_interface.create_account(role='host')
        if ok:
            self.log('Successfully added to hoster list!')
        else:
            self.error(result)
        self.refresh()

    @pyqtSlot()
    def upload_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Select file",
            directory=os.getenv('HOME', None) or os.getenv('HOMEPATH', None),
        )
        if filename:
            self.ws_send(
                {
                    "command": "upload",
                    "kwargs": {
                        "path": filename
                    }
                }
            )

    @pyqtSlot()
    def download_file(self, hash_):
        directory = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            directory=os.getenv('HOME', None) or os.getenv('HOMEPATH', None),
        )
        if not directory:
            self.log('Downloading cancelled.')
            return
        self.ws_send(
            {
                "command": "download",
                "kwargs": {
                    "destination": directory,
                    "hash": hash_
                }
            }
        )

    # noinspection PyUnresolvedReferences
    def choose_tokens_for_deposit(self, size, price_per_hour):
        dialog: QDialog = uic.loadUi(settings.ui_create_deposit_for_file)
        dialog.calendarWidget: QCalendarWidget
        dialog.deposit_size_input: QDoubleSpinBox

        # noinspection PyTypeChecker,PyCallByClass
        @pyqtSlot(float)
        def upd_date(value: float):
            try:
                deposit_end = datetime.now() + timedelta(hours=value // price_per_hour)
            except OverflowError:
                deposit_end = datetime.max
            deposit_end = QDate.fromString(deposit_end.strftime('%Y-%m-%d'), 'yyyy-MM-dd')
            dialog.calendarWidget.setSelectedDate(deposit_end)

        @pyqtSlot(QDate)
        def upd_value(date: QDate):
            deposit_end = date.toPyDate()
            hours = (deposit_end - datetime.now().date()).days * 24
            value = hours * price_per_hour
            dialog.deposit_size_input.setValue(value)

        if size < 1024:
            size = f'{size} B'
        elif size < 1024 ** 2:
            size = f'{size / 1024:.2f} KB'
        elif size < 1024 ** 3:
            size = f'{size / 1024 ** 2:.2f} MB'
        else:
            size = f'{size / 1024 ** 3:.2f} GB'
        dialog.file_size_display.setText(size)
        dialog.calendarWidget.clicked[QDate].connect(upd_value)
        dialog.deposit_size_input.valueChanged.connect(upd_date)

        if dialog.exec_():
            result = dialog.deposit_size_input.value()
            if not result:
                result = -1
        else:
            result = -1
        return self.ws_send({'status': 'success', 'result': result})

    @pyqtSlot()
    def enable_hosting_settings_controls(self):
        self.ui.settings_apply_btn.setEnabled(True)
        self.ui.settings_reset_btn.setEnabled(True)

    @pyqtSlot()
    def change_directory(self):
        directory = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            directory=os.getenv('HOME', None) or os.getenv('HOMEPATH', None),
        )
        if not directory:
            return
        self.ui.directory_input.setText(directory)

    @pyqtSlot()
    def apply_settings(self):
        disk_space = self.ui.disk_space_input.value()
        self.daemon_interface.set_disk_space_for_hosting(disk_space=disk_space)
        box_dir = self.ui.directory_input.text()
        self.daemon_interface.change_box_dir(box_dir=box_dir)

    @pyqtSlot()
    def reset_settings(self):
        self.refresh_settings_tab()

    @pyqtSlot(QEvent)
    def closeEvent(self, event):
        dialog: QDialog = uic.loadUi(settings.ui_submit_exit)
        if dialog.exec_():  # submitted
            # ToDo: running in tray
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
                password_dialog: QDialog = uic.loadUi(settings.ui_enter_password)
                password_dialog.password_input.setFocus()
                if not password_dialog.exec_():
                    self.shutdown()
                    sys.exit()
                password = password_dialog.password_input.text()
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
