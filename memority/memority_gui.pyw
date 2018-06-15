import multiprocessing
import sys

import asyncio
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from quamash import QEventLoop

from settings import settings as daemon_settings


def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    splash_pix = QPixmap(os.path.join(daemon_settings.base_dir, 'splashscreen.jpg'))
    splash = QSplashScreen(splash_pix)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.show()
    splash.showMessage('Processing imports', alignment=Qt.AlignBottom | Qt.AlignCenter, color=Qt.white)
    from main_window import MainWindow

    splash.showMessage('Starting application', alignment=Qt.AlignBottom | Qt.AlignCenter, color=Qt.white)
    w = MainWindow(event_loop=loop)
    splash.finish(w)

    loop.run_forever()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
