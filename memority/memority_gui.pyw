import errno
import sys

import contextlib
import json
import os
import requests
import socket
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta
from functools import partial

from memority_core import MemorityCore
from settings import settings as daemon_settings
from ui_settings import ui_settings

# from bugtracking import raven_client


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def file_size_human_readable(size):
    if size < 1024:
        size = f'{size} B'
    elif size < 1024 ** 2:
        size = f'{size / 1024:.2f} KB'
    elif size < 1024 ** 3:
        size = f'{size / 1024 ** 2:.2f} MB'
    else:
        size = f'{size / 1024 ** 3:.2f} GB'
    return size


def parse_date_from_string(d_: str):
    return datetime.strptime(d_[:-4], '%Y-%m-%d %H:%M').date()


class Worker(QThread):

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.memority_core = MemorityCore()

    def stop(self):
        self.memority_core.cleanup()

    def run(self):
        self.memority_core.run()


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

    def get_user_ip(self):
        result = requests.get(f'{self.daemon_address}/info/host_ip/').json()
        if result.get('status') == 'success':
            return result.get('data').get('host_ip')

    def get_space_used(self):
        result = requests.get(f'{self.daemon_address}/info/space_used/').json()
        if result.get('status') == 'success':
            return result.get('data').get('space_used')

    def set_disk_space_for_hosting(self, disk_space):
        requests.post(f'{self.daemon_address}/disk_space/', json={"disk_space": disk_space})

    def change_box_dir(self, box_dir):
        requests.post(f'{self.daemon_address}/change_box_dir/', json={"box_dir": box_dir})

    def get_file_metadata(self, file_hash):
        result = requests.get(f'{self.daemon_address}/files/{file_hash}/').json()
        if result.get('status') == 'success':
            return result.get('data')

    def prolong_deposit_for_file(self, file_hash, value):
        resp = requests.post(
            f'{self.daemon_address}/files/{file_hash}/deposit/',
            json={
                "value": value
            }
        )
        if resp.status_code == 200:
            return True, ...
        else:
            data = resp.json()
            msg = data.get('message')
            return False, f'Deposit creation failed.\n{msg}'

    def get_transactions(self):
        result = requests.get(f'{self.daemon_address}/transactions/').json()
        if result.get('status') == 'success':
            return result.get('data')


# noinspection PyArgumentList
class MainWindow(QMainWindow):
    daemon_started_signal = pyqtSignal(name="daemon_started_signal")

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon_interface = DaemonInterface(f'http://{daemon_settings.daemon_address}')
        self.ui: QWidget = uic.loadUi(ui_settings.ui_main_window)
        self.setup_ui()
        self.tray_icon = self.setup_tray_icon()
        self.tray_icon.show()
        self.ensure_addr_not_in_use()
        self.ws_client = QWebSocket()
        sg = QDesktopWidget().screenGeometry()
        widget = self.ui.geometry()
        self.ui.move(
            int((sg.width() - widget.width()) / 4),
            int((sg.height() - widget.height()) / 3)
        )
        self.daemon_started_signal.connect(self.on_daemon_started)
        self._worker = Worker()
        self._worker.start()
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.ping_daemon)
        self.timer.start()

    def ping_daemon(self):
        if self.daemon_interface.ping_daemon():
            self.daemon_started_signal.emit()

    def on_daemon_started(self):
        self.timer.stop()
        self.unlock_account()
        self.ws_client.error.connect(self.ws_error)
        self.ws_client.textMessageReceived.connect(self.ws_on_msg_received)
        self.ws_client.open(QUrl(f'ws://{daemon_settings.daemon_address}'))
        self.ui.show()
        self.refresh()

    def setup_ui(self):
        self.ui.closeEvent = self.closeEvent
        self.ui.buy_mmr_btn.hide()
        self.ui.transfer_mmr_btn.hide()

        self.ui.transaction_history_lbl.hide()
        self.ui.transaction_history_table.hide()
        header = self.ui.transaction_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

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
        self.ui.bulk_prolong_deposit_btn.clicked.connect(self.prolong_deposit_for_all_files)

    def setup_tray_icon(self):
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(QIcon(os.path.join(daemon_settings.base_dir, 'icon.ico')))

        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.ui.show)
        hide_action.triggered.connect(self.ui.hide)
        quit_action.triggered.connect(self.shutdown)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        tray_icon.setContextMenu(tray_menu)
        return tray_icon

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
        dialog: QDialog = uic.loadUi(ui_settings.ui_error_msg)
        dialog.msg.setText(
            f'<html><body>{msg}</html></body>'
        )
        dialog.adjustSize()
        dialog.exec_()

    def notify(self, msg):
        self.log(msg)
        msg = msg.replace('\n', '<br/>')
        dialog: QDialog = uic.loadUi(ui_settings.ui_info_msg)
        dialog.msg.setText(
            f'<html><body>{msg}</html></body>'
        )
        dialog.adjustSize()
        dialog.exec_()

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
        # region TX History
        self.ui.transaction_history_table: QTableWidget
        self.ui.transaction_history_table.setRowCount(0)  # clear table
        transactions = self.daemon_interface.get_transactions()
        if transactions:
            self.ui.transaction_history_lbl.show()
            self.ui.transaction_history_table.show()
        for tx in transactions:
            from_item = QTableWidgetItem(tx['from'] or '-')
            to_item = QTableWidgetItem(tx['to'])
            date_item = QTableWidgetItem(tx['date'])
            value_item = QTableWidgetItem(str(tx['value']))
            comment_item = QTableWidgetItem(tx['comment'])
            for item in [from_item, to_item, date_item, value_item, comment_item]:
                item.setToolTip(item.text())
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
            row_position = self.ui.transaction_history_table.rowCount()
            self.ui.transaction_history_table.insertRow(row_position)
            self.ui.transaction_history_table.setItem(row_position, 0, from_item)
            self.ui.transaction_history_table.setItem(row_position, 1, to_item)
            self.ui.transaction_history_table.setItem(row_position, 2, date_item)
            self.ui.transaction_history_table.setItem(row_position, 3, value_item)
            self.ui.transaction_history_table.setItem(row_position, 4, comment_item)
        # endregion

    def refresh_files_tab(self):
        self.ui.file_list_scrollarea_layout: QVBoxLayout
        self.ui.file_list_spacer: QSpacerItem
        files = self.daemon_interface.get_files()
        if not files:
            return
        self.clear_layout(self.ui.file_list_scrollarea_layout)
        for file in files:
            file_list_item = uic.loadUi(ui_settings.ui_file_list_item)
            file_list_item.uploaded_on_display.setText(file.get('timestamp'))
            file_list_item.name_display.setText(file.get('name'))
            file_list_item.hash_display.setText(file.get('hash'))
            file_list_item.size_display.setText(file_size_human_readable(file.get('size')))
            file_list_item.deposit_end_display.setText(file.get('deposit_ends_on'))
            file_list_item.download_btn.clicked.connect(partial(self.download_file, file.get('hash')))
            file_list_item.prolong_deposit_btn.clicked.connect(partial(self.prolong_deposit, file.get('hash')))
            self.ui.file_list_scrollarea_layout.addWidget(file_list_item)
        self.ui.file_list_scrollarea_layout.addItem(QSpacerItem(QSizePolicy.Expanding, QSizePolicy.Expanding, 0, 0))

    def refresh_hosting_tab(self):
        address = self.daemon_interface.get_user_address()
        ip = self.daemon_interface.get_user_ip() or 'Not in host list.'
        space_used = self.daemon_interface.get_space_used()
        self.ui.hosting_addr_display.setText(address)
        self.ui.hosting_ip_display.setText(ip)
        self.ui.hosting_space_display.setText(space_used)

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
        generate_address_dialog: QDialog = uic.loadUi(ui_settings.ui_generate_address)
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
        add_key_dialog: QDialog = uic.loadUi(ui_settings.ui_add_key)
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
        create_account_dialog: QDialog = uic.loadUi(ui_settings.ui_create_account)
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
    @pyqtSlot()
    def prolong_deposit(self, _hash):
        # noinspection PyTypeChecker,PyCallByClass
        @pyqtSlot(float)
        def upd_date(value: float):
            if value < price_per_hour * 24 * 14:
                dialog.deposit_size_input.setValue(price_per_hour * 24 * 14)
                return
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
            _value = hours * price_per_hour
            dialog.deposit_size_input.setValue(_value)

        def paint_cell(painter, rect, date):
            QCalendarWidget.paintCell(dialog.calendarWidget, painter, rect, date)
            if date == QDate(deposit_ends_on):
                color = dialog.calendarWidget.palette().color(QPalette.Highlight)
                color.setAlpha(128)
                painter.fillRect(rect, color)

        file_metadata = self.daemon_interface.get_file_metadata(file_hash=_hash)
        size = file_metadata.get('size')
        price_per_hour = file_metadata.get('price_per_hour')
        deposit_ends_on = datetime.strptime(file_metadata.get('deposit_ends_on', [])[:-4], '%Y-%m-%d %H:%M')

        dialog: QDialog = uic.loadUi(ui_settings.ui_create_deposit_for_file)
        dialog.calendarWidget: QCalendarWidget
        dialog.deposit_size_input: QDoubleSpinBox
        dialog.calendarWidget.setMinimumDate((deposit_ends_on + timedelta(weeks=2)).date())
        dialog.deposit_size_input.setValue(price_per_hour * 24 * 14)
        dialog.calendarWidget.paintCell = paint_cell
        dialog.calendarWidget.updateCells()

        size = file_size_human_readable(size)
        dialog.file_size_display.setText(size)
        dialog.calendarWidget.clicked[QDate].connect(upd_value)
        dialog.deposit_size_input.valueChanged.connect(upd_date)

        if dialog.exec_():
            input_value = dialog.deposit_size_input.value()
            self.log(f'Adding {input_value:.18f} MMR to deposit | file: {_hash}.\n'
                     f'Please wait...')
            ok, result = self.daemon_interface.prolong_deposit_for_file(file_hash=_hash, value=input_value)
            if ok:
                self.refresh_files_tab()
                self.notify('File deposit successfully updated.')
                self.log('File deposit successfully updated.')
            else:
                self.error(result)

    # noinspection PyUnresolvedReferences,PyReferencedBeforeAssignment
    @pyqtSlot()
    def prolong_deposit_for_all_files(self):
        @pyqtSlot(QDate)
        def upd_value(date: QDate):
            deposit_end_ = date.toPyDate()
            self.clear_layout(dialog.labels_layout)
            total_val = 0
            i = 0
            for i, file_ in enumerate(files):
                val_ = file_['price_per_hour'] \
                       * (deposit_end_ - parse_date_from_string(file_['deposit_ends_on'])).days * 24
                total_val += val_
                dialog.labels_layout.addWidget(
                    QLabel(f'to {file_["name"] if len(file_["name"]) < 64 else file_["name"][:64] + "..."}:'), i, 0
                )
                dialog.labels_layout.addWidget(
                    QLabel(f'{val_:.18f} MMR'), i, 1
                )
            dialog.total_val_display.setText(f'{total_val:.18f} MMR')
            dialog.labels_layout.addItem(QSpacerItem(QSizePolicy.Expanding, QSizePolicy.Expanding, 0, 0), i + 2, 0)

        def paint_cell(painter, rect, date: QDate):
            QCalendarWidget.paintCell(dialog.calendarWidget, painter, rect, date)
            for f in files:
                if date.toPyDate() == parse_date_from_string(f['deposit_ends_on']):
                    color = dialog.calendarWidget.palette().color(QPalette.Highlight)
                    color.setAlpha(128)
                    painter.fillRect(rect, color)
                    painter.drawText(rect.bottomLeft(), f['name'])

        files = self.daemon_interface.get_files()
        if not files:
            self.error('You don`t have files to prolong deposit.')
            return
        min_date = min(
            [
                parse_date_from_string(f['deposit_ends_on'])
                for f in files
            ]
        ) + timedelta(weeks=2)

        dialog: QDialog = uic.loadUi(ui_settings.ui_bulk_prolong_deposit)
        dialog.calendarWidget: QCalendarWidget
        dialog.labels_layout: QGridLayout
        dialog.calendarWidget.setMinimumDate(min_date)
        upd_value(QDate(min_date))
        dialog.calendarWidget.paintCell = paint_cell
        dialog.calendarWidget.updateCells()
        dialog.calendarWidget.clicked[QDate].connect(upd_value)

        if dialog.exec_():
            deposits = []
            for file in files:
                deposit_end = dialog.calendarWidget.selectedDate().toPyDate()
                val = file['price_per_hour'] * (deposit_end - parse_date_from_string(file['deposit_ends_on'])).days * 24
                if val:
                    deposits.append(
                        (
                            file['hash'],
                            val
                        )
                    )
            self.log(f'Adding {sum([d[1] for d in deposits]):.18f} MMR to deposits')
            for d in deposits:
                self.log(f'Adding {d[1]:.18f} MMR to deposit | file: {d[0]}. Please wait...')
                ok, result = self.daemon_interface.prolong_deposit_for_file(file_hash=d[0], value=d[1])
                if ok:
                    self.refresh_files_tab()
                    self.log('File deposit successfully updated.')
                else:
                    self.error(result)
            self.notify(f'Successfully updated deposits for {len(deposits)} files.')

    # noinspection PyUnresolvedReferences
    def choose_tokens_for_deposit(self, size, price_per_hour):
        dialog: QDialog = uic.loadUi(ui_settings.ui_create_deposit_for_file)
        dialog.calendarWidget: QCalendarWidget
        dialog.deposit_size_input: QDoubleSpinBox
        dialog.calendarWidget.setMinimumDate((datetime.now() + timedelta(weeks=2)).date())

        # noinspection PyTypeChecker,PyCallByClass
        @pyqtSlot(float)
        def upd_date(value: float):
            if value < price_per_hour * 24 * 14:
                dialog.deposit_size_input.setValue(price_per_hour * 24 * 14)
                return
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

        size = file_size_human_readable(size)
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
        dialog: QDialog = uic.loadUi(ui_settings.ui_submit_exit)
        if dialog.exec_():  # submitted
            self.shutdown()
            event.accept()
        else:
            event.ignore()

    def ensure_addr_not_in_use(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', daemon_settings.renter_app_port))
            s.close()
            del s
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', daemon_settings.hoster_app_port))
            s.close()
            del s
        except OSError as err:
            if err.errno == errno.EADDRINUSE:
                self.error(
                    'Ports are already in use!\n'
                    'Seems like Memority is already running or another application uses them.'
                )
                sys.exit(0)
            else:
                ...
                # raven_client.captureException()

    def unlock_account(self):
        if not self.daemon_interface.is_first_run():
            while True:
                password_dialog: QDialog = uic.loadUi(ui_settings.ui_enter_password)
                password_dialog.password_input.setFocus()
                if not password_dialog.exec_():
                    self.shutdown()
                    sys.exit()
                password = password_dialog.password_input.text()
                if self.daemon_interface.unlock_account(password):
                    break
                else:
                    self.error('Invalid password!')
                    continue

    @staticmethod
    def shutdown():
        qApp.quit()
        sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    w = MainWindow()
    sys.exit(app.exec_())
