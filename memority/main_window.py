import errno
import sys

import asyncio
import json
import os
import re
import socket
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta
from functools import partial

import utils
from bugtracking import raven_client
from memority_core import MemorityCore
from pyqt_requests import *
from settings import settings as daemon_settings, Settings
from ui_settings import ui_settings


def del_from_pool(func):
    def wrapper(pool: list, item, *args, **kwargs):
        del pool[pool.index(item)]
        del item
        return func(*args, **kwargs)

    return wrapper


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


# noinspection PyArgumentList
class MainWindow(QMainWindow):
    memority_core = None
    daemon_started = pyqtSignal()
    synced = pyqtSignal()
    request_pool = []

    def __init__(self, event_loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui: QWidget = uic.loadUi(ui_settings.ui_main_window)
        self.setup_ui()
        self.tray_icon = self.setup_tray_icon()
        self.tray_icon.show()
        self.ensure_addr_not_in_use()
        self.event_loop = event_loop
        self.ws_client = QWebSocket()
        self.ping_daemon_timer = QTimer(self)
        self.ping_daemon_timer.setInterval(1000)
        self.ping_daemon_timer.start()
        self.sync_status_timer = QTimer(self)
        self.sync_status_timer.setInterval(2000)
        self.connect_signals()
        sg = QDesktopWidget().screenGeometry()
        widget = self.ui.geometry()
        self.ui.move(
            int((sg.width() - widget.width()) / 4),
            int((sg.height() - widget.height()) / 3)
        )
        self.start_memority_core()

    def start_memority_core(self):
        self.memority_core = MemorityCore(event_loop=self.event_loop)
        if utils.check_first_run():
            self.memority_core.prepare()
            return
        while True:
            try:
                password_dialog: QDialog = uic.loadUi(ui_settings.ui_enter_password)
                password_dialog.password_input.setFocus()
                if not password_dialog.exec_():
                    self.shutdown()
                    return
                password = password_dialog.password_input.text()
                self.memority_core.set_password(password)
                break
            except Settings.InvalidPassword:
                self.error('Invalid password!')
                continue
        self.memority_core.prepare()

    def setup_ui(self):
        self.ui.closeEvent = self.closeEvent
        self.ui.buy_mmr_btn.hide()
        self.ui.transfer_mmr_btn.hide()

        self.ui.transaction_history_lbl.hide()
        self.ui.transaction_history_table.hide()
        self.ui.sync_display_widget.hide()
        self.ui.copy_address_btn.setDisabled(True)
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
        self.ui.become_miner_btn.clicked.connect(self.become_a_miner)
        self.ui.check_miner_request_status_btn.clicked.connect(self.check_miner_request_status)
        self.ui.directory_change_btn.clicked.connect(self.change_directory)
        self.ui.settings_apply_btn.clicked.connect(self.apply_settings)
        self.ui.settings_reset_btn.clicked.connect(self.reset_settings)
        self.ui.disk_space_input.valueChanged.connect(self.enable_hosting_settings_controls)
        self.ui.directory_input.textChanged.connect(self.enable_hosting_settings_controls)
        self.ui.upload_file_btn.clicked.connect(self.upload_file)
        self.ui.bulk_prolong_deposit_btn.clicked.connect(self.prolong_deposit_for_all_files)

    # noinspection PyUnresolvedReferences
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

    # noinspection PyUnresolvedReferences
    def connect_signals(self):
        self.ws_client.error.connect(self.ws_error)
        self.ws_client.textMessageReceived.connect(self.ws_on_msg_received)
        self.daemon_started.connect(self.on_daemon_started)
        self.synced.connect(self.on_synced)
        self.ping_daemon_timer.timeout.connect(self.ping_daemon)
        self.sync_status_timer.timeout.connect(self.update_sync_status)

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
                raven_client.captureException()

    def ping_daemon(self):
        @del_from_pool
        def done(started: bool):
            if started:
                self.daemon_started.emit()

        r = PingRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(done, self.request_pool, r))
        r.send()

    def update_sync_status(self):
        @del_from_pool
        @pyqtSlot()
        def got_sync_status(syncing: bool, percent: int):
            if syncing:
                self.ui.setDisabled(True)
                self.ui.sync_display_widget.show()
                self.ui.sync_progressbar.setValue(percent)
            else:
                self.sync_status_timer.stop()
                self.ui.setEnabled(True)
                self.ui.sync_display_widget.hide()
                self.synced.emit()

        r = GetSyncStatusRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_sync_status, self.request_pool, r))
        r.send()

    @pyqtSlot()
    def on_daemon_started(self):
        self.ping_daemon_timer.stop()
        self.sync_status_timer.start()
        self.refresh_wallet_tab()
        self.ws_client.open(QUrl(f'ws://{daemon_settings.daemon_address}/ws/'))
        self.ui.show()
        self.check_app_updates()

    @pyqtSlot()
    def on_synced(self):
        self.check_contract_updates()
        self.refresh()

    def check_contract_updates(self):
        @del_from_pool
        @pyqtSlot()
        def got_response(client_update_available: bool):
            if client_update_available:
                self.notify(
                    'Smart Contract needs update.\n'
                    'Please do not close the application while your data is transferring.'
                )
                self.ui.setDisabled(True)
                self.update_client_contract()

        r = CheckClientContractUpdatesRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_response, self.request_pool, r))
        r.send()

    def check_app_updates(self):
        @del_from_pool
        @pyqtSlot()
        def got_response(latest_version, download_url):
            if latest_version > daemon_settings.version:
                self.notify(
                    f'<html><body>'
                    f'<p>New version is available!</p>'
                    f'<p>You can download it on <a href={download_url}>{download_url}</a></p>'
                    f'</html></body>'
                )

        r = GetLatestVersionRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_response, self.request_pool, r))
        r.send()

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
        self.ui.log_widget.appendHtml(msg)
        self.ui.log_widget.moveCursor(QTextCursor.End)
        self.ui.log_widget.repaint()

    def error(self, msg: str):
        self.log(msg)

        msg = msg.replace('\n', '<br/>')

        for url in re.findall('(?:(?:https?|ftp)://)?[\w/\-?=%.]+\.[\w/\-?=%.]+', msg):
            msg = msg.replace(
                url,
                f'<a href="{url}" style="font-weight: bold; color: #fff">{url}</a>'
            )

        msg = f'<html><body>{msg}</html></body>'

        dialog: QDialog = uic.loadUi(ui_settings.ui_error_msg)
        dialog.msg.setText(msg)
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
                self.refresh_files_tab()
            elif data.get('details') == 'downloaded':
                self.notify('File successfully downloaded!')
                self.refresh_files_tab()
            elif data.get('details') == 'client_contract_updated':
                self.notify('Your data successfully transferred to new Smart Contract!')
                self.ui.setEnabled(True)
                self.refresh()
        elif status == 'error':
            self.error(data.get('message'))

    @pyqtSlot()
    def refresh(self):
        @del_from_pool
        @pyqtSlot()
        def done(roles: list):
            self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.My_files))
            self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.Hosting_statistics))
            self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.Settings))
            if 'client' in roles:
                self.ui.tabWidget.addTab(self.ui.My_files, "My files")
            if 'hoster' in roles:
                self.ui.tabWidget.addTab(self.ui.Hosting_statistics, "Hosting statistics")
            self.ui.tabWidget.addTab(self.ui.Settings, "Settings")
            self.refresh_wallet_tab()
            self.refresh_files_tab()
            self.refresh_hosting_tab()
            self.refresh_settings_tab()

        r = GetUserRoleRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(done, self.request_pool, r))
        r.send()

    def refresh_wallet_tab(self):
        @del_from_pool
        @pyqtSlot()
        def got_address(address: str):
            if address:
                self.ui.copy_address_btn.setEnabled(True)
            else:
                address = 'Please go to "Settings" - "Create account"'
            self.ui.address_display.setText(address)

        @del_from_pool
        @pyqtSlot()
        def got_balance(balance: float):
            self.ui.balance_display.setText(f'{balance} MMR')

        @del_from_pool
        @pyqtSlot()
        def got_transactions(transactions: list):
            self.ui.transaction_history_table: QTableWidget
            self.ui.transaction_history_table.setRowCount(0)  # clear table
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

        # region Address
        r = GetUserAddressRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_address, self.request_pool, r))
        r.send()
        # endregion

        # region Balance
        r = GetUserBalanceRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_balance, self.request_pool, r))
        r.send()
        # endregion

        # region TX History
        r = GetUserTransactionsRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_transactions, self.request_pool, r))
        r.send()
        # endregion

    def refresh_files_tab(self):
        @del_from_pool
        @pyqtSlot()
        def got_files(ok: bool, error: str, files: list):
            if not ok:
                self.error(error)
                return
            self.ui.file_list_scrollarea_layout: QVBoxLayout
            self.ui.file_list_spacer: QSpacerItem
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

        r = GetUserFilesRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_files, self.request_pool, r))
        r.send()

    def refresh_hosting_tab(self):
        @del_from_pool
        @pyqtSlot()
        def got_address(address: str):
            self.ui.hosting_addr_display.setText(address)

        @del_from_pool
        @pyqtSlot()
        def got_ip(ip: str):
            self.ui.hosting_ip_display.setText(ip or 'Not in host list.')

        @del_from_pool
        @pyqtSlot()
        def got_space_used(space_used: str):
            self.ui.hosting_space_display.setText(space_used)

        # region Address
        r = GetUserAddressRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_address, self.request_pool, r))
        r.send()
        # endregion

        # region IP
        r = GetUserIPRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_ip, self.request_pool, r))
        r.send()
        # endregion

        # region Space used
        r = GetSpaceUsedRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_space_used, self.request_pool, r))
        r.send()
        # endregion

    def refresh_settings_tab(self):
        @del_from_pool
        @pyqtSlot()
        def got_user_role(roles: list):
            for element in [
                self.ui.create_account_btn,
                self.ui.import_account_btn,
                self.ui.export_account_btn,
                self.ui.become_hoster_btn,
                self.ui.become_miner_btn,
                self.ui.check_miner_request_status_btn,
                self.ui.hosting_settings_widget
            ]:
                element.hide()
            self.ui.import_account_btn.show()
            if roles:
                self.ui.export_account_btn.show()
                if 'hoster' in roles:
                    self.ui.hosting_settings_widget.show()
                else:
                    self.ui.become_hoster_btn.show()
                if 'miner' not in roles:
                    if 'pending_miner' in roles:
                        self.ui.check_miner_request_status_btn.show()
                    else:
                        self.ui.become_miner_btn.show()
            else:
                self.ui.create_account_btn.show()

        @del_from_pool
        @pyqtSlot()
        def got_disk_space_for_hosting(disk_space_for_hosting: float):
            self.ui.disk_space_input.setValue(disk_space_for_hosting)

        @del_from_pool
        @pyqtSlot()
        def got_box_dir(box_dir: str):
            self.ui.directory_input.setText(box_dir)

        # region Role
        r = GetUserRoleRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_user_role, self.request_pool, r))
        r.send()
        # endregion

        # region Disk Space
        r = GetDiskSpaceForHostingRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_disk_space_for_hosting, self.request_pool, r))
        r.send()
        # endregion

        # region Box Dir
        r = GetBoxDirRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_box_dir, self.request_pool, r))
        r.send()
        # endregion

        self.ui.settings_apply_btn.setDisabled(True)
        self.ui.settings_reset_btn.setDisabled(True)

    @pyqtSlot()
    def copy_address_to_clipboard(self):
        self.ui.address_display: QLineEdit
        QApplication.clipboard().setText(self.ui.address_display.text())

    @pyqtSlot()
    def create_account(self):
        def _request_mmr():
            add_key_dialog: QDialog = uic.loadUi(ui_settings.ui_add_key)
            if not add_key_dialog.exec_():
                return
            self.log('Please wait while we’ll send you MMR tokens for testing, it may take a few minutes. '
                     'Do not close the application.')
            r = RequestMMRRequest(key=add_key_dialog.key_input.text())
            self.request_pool.append(r)
            r.finished.connect(partial(got_request_mmr_result, self.request_pool, r))
            r.send()

        def _create_account():
            create_account_dialog: QDialog = uic.loadUi(ui_settings.ui_create_account)
            if not create_account_dialog.exec_():
                return
            role = {
                0: 'client',
                1: 'host',
                2: 'both'
            }.get(create_account_dialog.role_input.currentIndex())

            self.log(f'Creating account for role "{role}"...\n'
                     f'This can take some time, as transaction is being written in blockchain.')
            if role in ['client', 'both']:
                self.log('Creating client account. When finished, the "My Files" tab appears.')
                r = CreateAccountRequest(role='client')
                self.request_pool.append(r)
                r.finished.connect(partial(got_create_client_result, self.request_pool, r))
                r.send()
            if role in ['host', 'both']:
                self.log('Creating hoster account. When finished, the "Hosting statistics" tab appears.')
                r = CreateAccountRequest(role='host')
                self.request_pool.append(r)
                r.finished.connect(partial(got_create_host_result, self.request_pool, r))
                r.send()

        @del_from_pool
        @pyqtSlot()
        def got_address_gen_result(ok: bool, result: str):
            if ok:
                self.log(f'Your address: {result}')
                self.refresh()
                nonlocal _request_mmr
                _request_mmr()
            else:
                self.error(result)

        @del_from_pool
        @pyqtSlot()
        def got_request_mmr_result(ok: bool, result: str):
            if ok:
                self.log(f'Tokens received. Your balance: {result} MMR')
                self.refresh()
                nonlocal _create_account
                _create_account()
            else:
                self.error(result)

        @del_from_pool
        @pyqtSlot()
        def got_create_client_result(ok: bool, result: str):
            if ok:
                self.log('Client account successfully created!')
                self.refresh()
            else:
                self.error(result)

        @del_from_pool
        @pyqtSlot()
        def got_create_host_result(ok: bool, result: str):
            if ok:
                self.log('Hoster account successfully created!')
                self.refresh()
            else:
                self.error(result)

        # region Ask for password and generate address
        generate_address_dialog: QDialog = uic.loadUi(ui_settings.ui_generate_address)
        if not generate_address_dialog.exec_():
            return
        password1 = generate_address_dialog.password1.text()
        password2 = generate_address_dialog.password2.text()

        if password1 != password2:
            self.error('Passwords don`t match!')
            return

        self.log(f'Generating address...')
        r = GenerateAddressRequest(password=password1)
        self.request_pool.append(r)
        r.finished.connect(partial(got_address_gen_result, self.request_pool, r))
        r.send()
        # endregion

    @pyqtSlot()
    def import_account(self):
        @del_from_pool
        @pyqtSlot()
        def got_importing_result(ok: bool, result: str):
            if ok:
                self.log('Account successfully imported!')
                self.unlock_account()  # ToDo: fix
            else:
                self.error(result)

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Select account file",
            os.path.join(os.getenv('HOME', None) or os.getenv('HOMEPATH', None), 'memority_account.bin'),
            "*.bin"
        )
        if filename:
            self.log('Importing account...')
            r = ImportAccountRequest(filename=filename)
            self.request_pool.append(r)
            r.finished.connect(partial(got_importing_result, self.request_pool, r))
            r.send()

    @pyqtSlot()
    def export_account(self):
        @del_from_pool
        @pyqtSlot()
        def got_exporting_result(ok: bool, result: str):
            if ok:
                self.log('Account successfully exported!')
            else:
                self.error(result)

        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Select a location to save your account file.",
            os.path.join(os.getenv('HOME', None) or os.getenv('HOMEPATH', None), 'memority_account.bin'),
            "*.bin"
        )
        if filename:
            self.log('Exporting account...')
            r = ExportAccountRequest(filename=filename)
            self.request_pool.append(r)
            r.finished.connect(partial(got_exporting_result, self.request_pool, r))
            r.send()

    @pyqtSlot()
    def become_a_hoster(self):
        @del_from_pool
        @pyqtSlot()
        def got_create_host_result(ok: bool, result: str):
            if ok:
                self.log('Successfully added to hoster list!')
            else:
                self.error(result)
            self.refresh()

        self.log('Adding your address and IP to contract...\n'
                 'This can take some time, as transaction is being written in blockchain.\n'
                 'When finished, the "Hosting statistics" tab appears.')

        r = CreateAccountRequest(role='host')
        self.request_pool.append(r)
        r.finished.connect(partial(got_create_host_result, self.request_pool, r))
        r.send()

    @pyqtSlot()
    def become_a_miner(self):
        @del_from_pool
        @pyqtSlot()
        def got_response(ok: bool, result: str):
            if ok:
                self.log(f'The request was successfully sent. Request status: {result}.')
            else:
                self.error(result)
            self.refresh()

        self.log('Sending request for adding you to miner list...')

        r = MinerStatusRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_response, self.request_pool, r))
        r.send()

    @pyqtSlot()
    def check_miner_request_status(self):
        @del_from_pool
        @pyqtSlot()
        def got_response(ok: bool, result: str):
            if ok:
                self.log(f'Request status: {result}.')
                if result == 'active':
                    self.notify('Please restart the application to start mining.')
            else:
                self.error(result)
            self.refresh()

        self.log('Sending request for miner request status...')

        r = MinerStatusRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_response, self.request_pool, r))
        r.send()

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
                    "file_hash": hash_
                }
            }
        )

    @pyqtSlot()
    def update_client_contract(self):
        self.ws_send(
            {
                "command": "update_client_contract"
            }
        )

    @pyqtSlot()
    def prolong_deposit(self, _hash):
        # noinspection PyUnresolvedReferences
        @del_from_pool
        @pyqtSlot()
        def got_file_metadata(file_metadata: dict):
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
                hours = (deposit_end - deposit_ends_on.date()).days * 24
                _value = hours * price_per_hour
                dialog.deposit_size_input.setValue(_value)

            def paint_cell(painter, rect, date):
                QCalendarWidget.paintCell(dialog.calendarWidget, painter, rect, date)
                if date == QDate(deposit_ends_on):
                    color = dialog.calendarWidget.palette().color(QPalette.Highlight)
                    color.setAlpha(128)
                    painter.fillRect(rect, color)

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
                r = ProlongDepositForFileRequest(file_hash=_hash, value=input_value)
                self.request_pool.append(r)
                r.finished.connect(partial(got_prolong_deposit_resp, self.request_pool, r))
                r.send()

        @del_from_pool
        @pyqtSlot()
        def got_prolong_deposit_resp(ok, result):
            if ok:
                self.refresh_files_tab()
                self.notify('File deposit successfully updated.')
            else:
                self.error(result)

        r = GetFileMetadataRequest(file_hash=_hash)
        self.request_pool.append(r)
        r.finished.connect(partial(got_file_metadata, self.request_pool, r))
        r.send()

    # noinspection PyUnresolvedReferences,PyReferencedBeforeAssignment
    @pyqtSlot()
    def prolong_deposit_for_all_files(self):
        # noinspection PyUnresolvedReferences
        @del_from_pool
        @pyqtSlot()
        def got_file_list(ok: bool, error: str, files: list):
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

            if not ok:
                self.error(error)
                return

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
                    val = file['price_per_hour'] * (
                            deposit_end - parse_date_from_string(file['deposit_ends_on'])).days * 24
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
                    r = ProlongDepositForFileRequest(file_hash=_hash, value=input_value)
                    self.request_pool.append(r)
                    r.finished.connect(partial(got_prolong_deposit_resp, self.request_pool, r))
                    r.send()

        @del_from_pool
        @pyqtSlot()
        def got_prolong_deposit_resp(ok, result):
            if ok:
                self.refresh_files_tab()
                self.notify('File deposit successfully updated.')
            else:
                self.error(result)

        r = GetUserFilesRequest()
        self.request_pool.append(r)
        r.finished.connect(partial(got_file_list, self.request_pool, r))
        r.send()

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
        dialog.deposit_size_input.setValue(price_per_hour * 24 * 14)
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
        @del_from_pool
        @pyqtSlot()
        def got_resp(ok, result):
            if ok:
                self.refresh_settings_tab()
            else:
                self.error(result)

        # region Disk space for hosting
        disk_space = self.ui.disk_space_input.value()
        r = SetDiskSpaceForHostingRequest(disk_space=disk_space)
        self.request_pool.append(r)
        r.finished.connect(partial(got_resp, self.request_pool, r))
        r.send()
        # endregion

        # region Box dir
        box_dir = self.ui.directory_input.text()
        r = ChangeBoxDirRequest(box_dir=box_dir)
        self.request_pool.append(r)
        r.finished.connect(partial(got_resp, self.request_pool, r))
        r.send()
        # endregion

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

    def shutdown(self):
        self.ui.hide()
        if hasattr(self, 'sync_status_timer'):
            self.sync_status_timer.stop()
        self.memority_core.cleanup()
        for task in asyncio.Task.all_tasks():
            task.cancel()
        qApp.quit()
        self.event_loop.stop()
        self.event_loop.close()
        sys.exit(0)
