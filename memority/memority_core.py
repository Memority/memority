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

import smart_contracts
from bugtracking import raven_client
from hoster.server import create_hoster_app
from logger import setup_logging
from models import db_manager
from renter.server import create_renter_app
from settings import settings
from smart_contracts.smart_contract_api import w3, import_private_key_to_eth, token_contract, client_contract, \
    memo_db_contract
from tasks import create_celery_processes
from utils import ask_for_password

locale.setlocale(locale.LC_ALL, '')

SYNC_STARTED = False


def process_line(line):
    if isinstance(line, bytes):
        line = line.decode('utf-8')
    if line:
        if 'Block synchronisation started' in line:
            global SYNC_STARTED
            SYNC_STARTED = True
        print(line.strip())


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(process_line(line))
    out.close()


class MemorityCore:
    hoster_app = None
    hoster_app_handler = None
    hoster_server = None
    p = None
    q = None
    renter_app = None
    renter_app_handler = None
    renter_server = None
    t = None
    celery_processes = []

    def __init__(self, *, event_loop=None, _password=None, _run_geth=True) -> None:
        if not event_loop:
            event_loop = asyncio.new_event_loop()
        self.event_loop = event_loop
        self.password = _password

        self.run_geth = _run_geth

    def run(self):
        # noinspection PyBroadException
        try:
            self.prepare()
            self.event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            raven_client.captureException()
        finally:
            self.cleanup()

    def prepare(self):
        db_manager.ensure_db_up_to_date()

        if self.run_geth:
            print('Starting geth...')
            if not os.path.isdir(settings.blockchain_dir):  # geth not initialized
                self.init_geth()
            self.start_geth_subprocess_handling_in_thread()

        if self.password:  # debug only
            settings.unlock(self.password)
            smart_contracts.smart_contract_api.ask_for_password = partial(ask_for_password, self.password)
            if settings.address:
                if settings.address.lower() not in [a.lower() for a in w3.eth.accounts]:
                    import_private_key_to_eth(password=self.password)

        setup_logging()
        self.configure_apps()

        self.celery_processes = create_celery_processes()

        for p in self.celery_processes:
            p.start()

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

        args = [
            settings.geth_executable,
            '--datadir', settings.blockchain_dir,
            '--port', '30320',
            '--networkid', '232019',
            '--identity', 'mmr_chain_v1',
            '--nodiscover'
        ]

        if settings.mining_status == 'active':
            password_file = '$NODE_DIR/password.txt'  # ToDo: NamedTemporaryFile
            if os.path.isfile(password_file):
                args = [
                    *args,
                    '--unlock', settings.address,
                    '--password', password_file,
                    '--mine'
                ]

        self.p = subprocess.Popen(
            args,
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
                print(line.strip().encode('utf-8'))
            if 'IPC endpoint opened' in line:
                geth_ipc_path = line[line.index('=') + 1:].strip()
                print('Geth IPC file path:', geth_ipc_path)
                if platform_name.lower() == 'windows':
                    geth_ipc_path = geth_ipc_path.replace('\\\\', '\\')
                geth_ipc_path = geth_ipc_path.replace('"', '')
                geth_ipc_path = geth_ipc_path.replace("'", '')
                settings.w3_url = geth_ipc_path
                smart_contracts.smart_contract_api.utils.w3 = smart_contracts.smart_contract_api.utils.create_w3()
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
        with contextlib.suppress(RuntimeError, AttributeError):
            print('Servers...')
            self.hoster_server.cancel()
            asyncio.ensure_future(self.hoster_app.shutdown())
            asyncio.ensure_future(self.hoster_app_handler.shutdown(60.0))
            asyncio.ensure_future(self.hoster_app.cleanup())

            self.renter_server.cancel()
            asyncio.ensure_future(self.renter_app.shutdown())
            asyncio.ensure_future(self.renter_app_handler.shutdown(60.0))
            asyncio.ensure_future(self.renter_app.cleanup())
        print('Servers closed.')
        if self.p:
            print('Geth...')
            self.p.terminate()
            self.p.wait()

        print('Celery processes...')
        for p in self.celery_processes:
            p.terminate()
        for p in self.celery_processes:
            p.join()

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
