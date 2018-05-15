import errno
import sys

import asyncio
import os
import socket
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from contextlib import redirect_stdout, redirect_stderr
from memority_core import MemorityCore
from quamash import QEventLoop

from bugtracking import raven_client
from settings import settings


class R:

    def __init__(self, logger_widget) -> None:
        self.logger_widget = logger_widget

    def write(self, msg):
        if msg.strip():
            self.logger_widget.appendPlainText(msg.strip())
            self.logger_widget.moveCursor(QTextCursor.End)


class MainWindow(QMainWindow):

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


if __name__ == "__main__":
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
            QMessageBox().critical(
                None,
                'Error!',
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
        _password=None,
        _run_geth=True
    )
    main_window = MainWindow(memority_core)
    with redirect_stdout(R(main_window.logger)):
        with redirect_stderr(R(main_window.logger)):
            memority_core.run()
