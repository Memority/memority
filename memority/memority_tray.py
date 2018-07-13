import errno
import sys

import asyncio
import os
import re
import socket
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from contextlib import redirect_stdout, redirect_stderr
from quamash import QEventLoop

from bugtracking import raven_client
from memority_core import MemorityCore
from settings import settings
from ui_settings import ui_settings


class R:

    def __init__(self, logger_widget) -> None:
        self.logger_widget = logger_widget

    def write(self, msg):
        if msg.strip():
            self.logger_widget.appendPlainText(msg.strip())
            self.logger_widget.moveCursor(QTextCursor.End)
            self.logger_widget.repaint()


class LoggerWindow(QMainWindow):

    def __init__(self, _memority_core, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memority_core = _memority_core

        self.setMinimumSize(QSize(1024, 480))
        self.setWindowTitle("Memority Core")
        self.logger = QPlainTextEdit()
        self.logger.setReadOnly(True)
        self.logger.document().setMaximumBlockCount(10000)
        self.setCentralWidget(self.logger)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(settings.base_dir, 'icon.ico')))

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def quit(self):
        self.memority_core.cleanup()
        qApp.quit()
        sys.exit(0)


def error(msg):
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


def run():
    app = QApplication(sys.argv)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', settings.renter_app_port))
        s.close()
        del s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', settings.hoster_app_port))
        s.close()
        del s
    except OSError as err:
        if err.errno == errno.EADDRINUSE:
            error(
                'Ports are already in use!\n'
                'Seems like Memority Core is already running or another application uses them.'
            )
            sys.exit(0)
        else:
            raven_client.captureException()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    memority_core = MemorityCore(
        event_loop=loop,
        _run_geth=True
    )
    password = settings.load_locals().get('password')
    if password:
        try:
            memority_core.set_password(password)
            return
        except settings.InvalidPassword:
            error('Invalid password in settings file!')
    while True:
        try:
            password_dialog: QDialog = uic.loadUi(ui_settings.ui_enter_password)
            password_dialog.password_input.setFocus()
            if not password_dialog.exec_():
                sys.exit(0)
            password = password_dialog.password_input.text()
            memority_core.set_password(password)
            break
        except settings.InvalidPassword:
            error('Invalid password!')
            continue

    main_window = LoggerWindow(memority_core)
    with redirect_stdout(R(main_window.logger)):
        with redirect_stderr(R(main_window.logger)):
            memority_core.run()


if __name__ == '__main__':
    run()
