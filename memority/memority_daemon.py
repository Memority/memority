#! /usr/bin/env python3
import os
import platform


def run_in_terminal():
    import memority_core
    memority_core.run()


def run_in_tray():
    import memority_tray
    memority_tray.run()


if __name__ == "__main__":
    if platform.system() == 'Linux' and not os.getenv('DISPLAY'):
        run_in_terminal()
    else:
        run_in_tray()
