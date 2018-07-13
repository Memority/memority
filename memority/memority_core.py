#! /usr/bin/env python3
import sys

import asyncio
import contextlib
import getpass
import locale
import logging
import os
import platform
import subprocess
import traceback
from queue import Queue
from shutil import copyfile
from tempfile import NamedTemporaryFile
from threading import Thread

from bugtracking import raven_client
from hoster.server import create_hoster_app
from logger import setup_logging
from models import db_manager
from renter.server import create_renter_app
from settings import settings, Settings
from smart_contracts.smart_contract_api import token_contract, client_contract, \
    memo_db_contract
from smart_contracts.smart_contract_api.utils import create_w3
from tasks import create_celery_processes, check_miner_status, update_miner_list, update_enodes
from utils import check_first_run

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger('memority')


def process_line(line):
    if isinstance(line, bytes):
        line = line.decode('utf-8')
    if line:
        if 'Block synchronisation started' in line:
            settings.SYNC_STARTED = True
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
    password = None
    password_file = None
    q = None
    renter_app = None
    renter_app_handler = None
    renter_server = None
    t = None
    celery_processes = []

    def __init__(self, *, event_loop=None, _run_geth=True) -> None:
        if not event_loop:
            event_loop = asyncio.new_event_loop()
        self.event_loop = event_loop

        self.run_geth = _run_geth

    def set_password(self, password):
        self.password = password
        settings.unlock(password)

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
        settings.SYNC_STARTED = False
        db_manager.ensure_db_up_to_date()

        if self.run_geth:
            print('Starting geth...')
            if not os.path.isdir(settings.blockchain_dir):  # geth not initialized
                self.init_geth()
            self.start_geth_subprocess_handling_in_thread()

        setup_logging()
        self.configure_apps()

        self.celery_processes = create_celery_processes()

        for p in self.celery_processes:
            p.start()

        if settings.mining_status == 'active':
            self.start_mining()

        check_miner_status.apply_async(countdown=10)
        update_miner_list.apply_async(countdown=10)
        update_enodes.apply_async(countdown=10)

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

        if self.password:
            self.password_file = NamedTemporaryFile(delete=False)  # tempfile.mkstemp?
            self.password_file.write(bytes(self.password, encoding='utf-8'))
            self.password_file.close()
            args += [
                '--unlock', settings.address,
                '--password', self.password_file.name,
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
        if self.password_file:
            print('Password file...')
            os.unlink(self.password_file.name)
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

    @staticmethod
    def start_mining():
        logger.info('Starting mining...')
        w3 = create_w3()
        w3.miner.start(1)
        logger.info('Mining started.')


ON_POSIX = 'posix' in sys.builtin_module_names

platform_name = platform.system()


def run():
    loop = asyncio.get_event_loop()

    _password, run_geth = None, False
    if '--docker' in sys.argv:
        _password = next(sys.stdin).strip()  # dev
    if '--no-geth-subprocess' not in sys.argv:
        run_geth = True

    if not _password:
        _password = settings.load_locals().get('password')

    if not _password and not check_first_run():
        _password = getpass.getpass()

    memority_core = MemorityCore(
        event_loop=loop,
        _run_geth=run_geth
    )
    try:
        memority_core.set_password(_password)
    except Settings.InvalidPassword:
        print('Invalid password.')
    else:
        memority_core.run()


if __name__ == '__main__':
    run()
