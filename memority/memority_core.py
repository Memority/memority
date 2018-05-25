#! /usr/bin/env python
import sys

import asyncio
import contextlib
import locale
import os
import platform
import subprocess
import traceback
from functools import partial
from queue import Queue
from shutil import copyfile
from threading import Thread

import renter
import smart_contracts
# from bugtracking import raven_client
from hoster.server import create_hoster_app
from logger import setup_logging
from renter.server import create_renter_app
from settings import settings
from smart_contracts.smart_contract_api import w3, import_private_key_to_eth, token_contract, client_contract, \
    memo_db_contract
from utils import ask_for_password

locale.setlocale(locale.LC_ALL, '')


def process_line(line):
    if isinstance(line, bytes):
        line = line.decode('utf-8')
    if line:
        print(line.strip())
    if 'Block synchronisation started' in line:
        renter.server.STATE = 1
    if 'Imported new chain segment' in line:
        renter.server.STATE = 2
    if 'Database closed' in line:
        sys.exit(0)


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(process_line(line))
    out.close()


class MemorityCore:
    def __init__(self, *, event_loop=None, _password=None, _run_geth=True) -> None:
        if not event_loop:
            event_loop = asyncio.new_event_loop()
        self.event_loop = event_loop
        self.password = _password
        self.run_geth = _run_geth
        self.q = None
        self.t = None
        self.p = None
        self.renter_app = None
        self.renter_app_handler = None
        self.renter_server = None
        self.hoster_app = None
        self.hoster_app_handler = None
        self.hoster_server = None

    def run(self):
        # noinspection PyBroadException
        try:
            self.prepare()
            self.event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            # raven_client.captureException()
        finally:
            self.cleanup()

    def prepare(self):
        if self.password:  # debug only
            settings.unlock(self.password)
            smart_contracts.smart_contract_api.ask_for_password = partial(ask_for_password, self.password)
            if settings.address:
                if settings.address.lower() not in [a.lower() for a in w3.eth.accounts]:
                    import_private_key_to_eth(password=self.password)

        if self.run_geth:
            print('Starting geth...')
            if not os.path.isdir(settings.blockchain_dir):  # geth not initialized
                self.init_geth()
            self.start_geth_subprocess_handling_in_thread()

        setup_logging()
        self.configure_apps()

    @staticmethod
    def init_geth():
        print('Geth is not initialized!\n'
              'Initializing Geth...')
        geth_init_sp = subprocess.Popen(
            [settings.geth_executable,
             '--datadir', settings.blockchain_dir,
             'init', settings.geth_init_json],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            close_fds=ON_POSIX
        )
        geth_init_sp.wait()
        out, err = geth_init_sp.communicate()
        print(out)
        if err:
            print(err)
            sys.exit(1)
        copyfile(
            src=settings.geth_static_nodes_json,
            dst=os.path.join(settings.blockchain_dir, 'geth', 'static-nodes.json'),
        )

    def start_geth_subprocess_handling_in_thread(self):
        if ON_POSIX:
            startupinfo = None
            creationflags = 0
        else:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        self.p = subprocess.Popen(
            [settings.geth_executable,
             '--datadir', settings.blockchain_dir,
             '--port', '30320',
             '--networkid', '232019',
             '--identity', 'mmr_chain_v1',
             '--nodiscover'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            startupinfo=startupinfo,
            creationflags=creationflags
        )
        while True:
            line = self.p.stdout.readline()
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            if line:
                print(line.strip())
            if 'IPC endpoint opened' in line:
                geth_ipc_path = line[line.index('=') + 1:].strip()
                print('Geth IPC file path:', geth_ipc_path)
                if platform_name.lower() == 'windows':
                    geth_ipc_path = geth_ipc_path.replace('\\\\', '\\')
                geth_ipc_path = geth_ipc_path.replace('"', '')
                geth_ipc_path = geth_ipc_path.replace("'", '')
                settings.w3_url = geth_ipc_path
                smart_contracts.smart_contract_api.w3 = smart_contracts.smart_contract_api.create_w3()
                token_contract.reload()
                client_contract.reload()
                memo_db_contract.reload()
                break
        self.q = Queue()
        self.t = Thread(target=enqueue_output, args=(self.p.stdout, self.q), daemon=True)
        self.t.start()

    def configure_apps(self):
        # region Hoster app configuration
        self.hoster_app = create_hoster_app()
        self.hoster_app_handler = self.hoster_app.make_handler()
        hoster_app_coroutine = self.event_loop.create_server(
            self.hoster_app_handler,
            settings.hoster_app_host,
            settings.hoster_app_port
        )
        self.hoster_server = asyncio.run_coroutine_threadsafe(hoster_app_coroutine, self.event_loop)
        print(f'Hoster App started on http://{settings.hoster_app_host}:{settings.hoster_app_port}')
        # endregion

        # region Renter app configuration
        self.renter_app = create_renter_app()
        self.renter_app_handler = self.renter_app.make_handler()
        renter_app_coroutine = self.event_loop.create_server(
            self.renter_app_handler,
            settings.renter_app_host,
            settings.renter_app_port
        )
        self.renter_server = asyncio.run_coroutine_threadsafe(renter_app_coroutine, self.event_loop)
        print(f'Renter App started on http://{settings.renter_app_host}:{settings.renter_app_port}')
        # endregion

    def cleanup(self, *args, **kwargs):
        print('Cleanup...')
        # with contextlib.suppress(RuntimeError, AttributeError):
        print('Servers...')
        self.hoster_server.cancel()
        self.event_loop.run_until_complete(self.hoster_app.shutdown())
        self.event_loop.run_until_complete(self.hoster_app_handler.shutdown(60.0))
        self.event_loop.run_until_complete(self.hoster_app.cleanup())

        self.renter_server.cancel()
        self.event_loop.run_until_complete(self.renter_app.shutdown())
        self.event_loop.run_until_complete(self.renter_app_handler.shutdown(60.0))
        self.event_loop.run_until_complete(self.renter_app.cleanup())
        print('Servers closed.')
        if self.p:
            print('Geth...')
            self.p.terminate()
            self.p.wait()
        print('Done.')


ON_POSIX = 'posix' in sys.builtin_module_names

platform_name = platform.system()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    password, run_geth = None, False
    if '--docker' in sys.argv:
        password = next(sys.stdin).strip()  # dev
    if '--no-geth-subprocess' not in sys.argv:
        run_geth = True

    memority_core = MemorityCore(
        event_loop=loop,
        _password=password,
        _run_geth=run_geth
    )
    memority_core.run()
