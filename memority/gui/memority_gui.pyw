#! /usr/bin/env python

import sys

import aiohttp
import asyncio
import contextlib
import json
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from asyncio import CancelledError
from quamash import QEventLoop

from bugtracking import raven_client
from dialogs import ask_for_password
from handlers import process_ws_message, error_handler
from settings import settings
from tabs import TabsWidget
from utils import unlock_account


class MainWindow(QMainWindow):

    def __init__(self, event_loop: QEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ws = None
        self.session = aiohttp.ClientSession()
        self.event_loop = event_loop
        self.resize(1024, 600)
        self.setWindowTitle('Memority GUI')

        container = QWidget(self)
        self.setCentralWidget(container)

        self.msg_for_testers = QLabel(
            """
            <p>This is an Alpha version of Memority app. It might be unstable, have bugs and errors.</p>
            <p>Please keep in mind that in some cases your stored data may be lost, 
            although we`ll do everything in our power to prevent this.</p>
            <p>If you`ve encountered a bug, please see if there is a new version on 
            <a href="https://memority.io/">https://memority.io</a>. Perhaps we have already fixed it. 
            If not, send us a report to 
            <a href="mailto:support@memority.io">support@memority.io</a>.</p>
            <p>You can see the instructions on how to use the application on 
            <a href="https://memority.io/how-to-use-app/">https://memority.io/how-to-use-app/</a>.</p>
            """
        )
        self.msg_for_testers.setOpenExternalLinks(True)
        self.log_widget = QPlainTextEdit()
        self.table_widget = TabsWidget(self)
        self.log_widget.setReadOnly(True)
        self.add_file_list_item = self.table_widget.tab_files.files_list_widget.add_item
        self.cleanup_file_list = self.table_widget.tab_files.files_list_widget.cleanup_file_list
        self.table_widget.tab_files.controls_widget.uploadButton.clicked.connect(
            self.open_file_dialog
        )

        main_layout = QVBoxLayout(container)
        main_layout.addWidget(self.msg_for_testers)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(self.log_widget)
        container.setLayout(main_layout)

        sg = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = int((sg.width() - widget.width()) / 4)
        y = int((sg.height() - widget.height()) / 3)
        self.move(x, y)
        asyncio.ensure_future(self.refresh())
        self.show()

    async def refresh(self):
        # while True:
        await self.table_widget.refresh()
        await self.table_widget.tab_settings.refresh()
        await self.table_widget.tab_wallet.info_widget.refresh()
        await self.table_widget.tab_hosting.refresh()
        await self.show_files()
        # await asyncio.sleep(5)

    def resizeEvent(self, event):
        self.log_widget.setFixedHeight(self.height() * .2)
        return super().resizeEvent(event)

    def open_file_dialog(self):
        dialog = QFileDialog()
        options = dialog.Options()
        filename, _ = dialog.getOpenFileName(self, options=options)
        # asyncio.ensure_future(self.show_progressbar())
        if filename:
            asyncio.ensure_future(self.ws_send(
                {
                    "command": "upload",
                    "kwargs": {
                        "path": filename
                    }
                }
            ))

    def download_file(self, path, hash_):
        asyncio.ensure_future(self.ws_send(
            {
                "command": "download",
                "kwargs": {
                    "destination": path,
                    "hash": hash_
                }
            }
        ))

    async def ws_handler(self):
        # ToDo: use QtWebSockets.QWebSocket, without asyncio
        try:
            session = aiohttp.ClientSession()
            self._ws = await session.ws_connect(settings.daemon_address, timeout=0, receive_timeout=0)
            async for msg in self._ws:
                if isinstance(msg, aiohttp.WebSocketError):
                    error_handler(str(msg))
                    continue
                data = json.loads(msg.data)
                process_ws_message(data, self)
        except CancelledError:
            pass
        except Exception as err:
            raven_client.captureException()
            error_handler(str(err))

    async def ws_send(self, data: dict):
        await self._ws.send_json(data)

    async def show_files(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{settings.daemon_address}/files/') as resp:
                data = await resp.json()
                process_ws_message(data, self)

    def closeEvent(self, event):
        reply = QMessageBox().question(
            self,
            "Are you sure to quit?",
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            asyncio.ensure_future(self._ws.close())
            asyncio.ensure_future(self.session.close())
            for task in asyncio.Task.all_tasks():
                task.cancel()
            self.event_loop.stop()

            event.accept()

        else:
            event.ignore()


def check_first_run():
    r = requests.get(f'{settings.daemon_address}/check_first_run/')
    return r.json().get('result')


def ping_daemon():
    try:
        r = requests.get(f'{settings.daemon_address}/ping/')
        if r.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False


def check_if_daemon_running():
    while True:
        daemon_running = ping_daemon()
        if daemon_running:
            break
        else:
            _app = QApplication(sys.argv)
            _app.setAttribute(Qt.AA_EnableHighDpiScaling)
            if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
                _app.setAttribute(Qt.AA_UseHighDpiPixmaps)

            _ok = QMessageBox().question(
                None,
                "Is the Memority Core running?",
                f'Can`t connect to Memority Core. Is it running?\n'
                f'Please launch Memority Core before Memority UI.\n'
                f'If you have already started Memority Core, wait a few seconds and try again.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            del _app
            if _ok != QMessageBox.Yes:
                sys.exit()


if __name__ == '__main__':
    check_if_daemon_running()
    _app = QApplication(sys.argv)
    _app.setAttribute(Qt.AA_EnableHighDpiScaling)
    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        _app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    if not check_first_run():
        while True:
            password, ok = ask_for_password('Password:')
            if not ok:
                sys.exit()
            if not unlock_account(password):
                continue
            break
        del _app

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    try:
        main_window = MainWindow(loop)
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(main_window.ws_handler())
    except Exception as err:
        raven_client.captureException()
        error_handler(str(err))
