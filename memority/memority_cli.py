#! /usr/bin/env python3
import os

import argparse
import asyncio
import collections
from typing import List

from cli import *


# region To implement
def import_account(args):
    print('Not implemented.')  # ToDo: implement


def get_host_status(args):
    print('Not implemented.')  # ToDo: implement


def get_host_ip(args):
    print('Not implemented.')  # ToDo: implement


def get_storage_info(args):
    print('Not implemented.')  # ToDo: implement


def resize_storage(args):
    print('Not implemented.')  # ToDo: implement


def set_box_dir(args):
    print('Not implemented.')  # ToDo: implement


def get_miner_status(args):
    print('Not implemented.')  # ToDo: implement


def get_miner_ip(args):
    print('Not implemented.')  # ToDo: implement


# endregion


ParserArgument = collections.namedtuple('ParserArgument', ['name', 'help', 'default'])


def add_parser_with_func(root, name, func, help_):
    parser = root.add_parser(name, help=help_)
    parser.set_defaults(func=func)
    return parser


def add_parser_with_args(root, name, func, help_, args: List[ParserArgument]):
    parser = add_parser_with_func(root, name, func, help_)
    for arg in args:
        if arg.default is not None:
            parser.add_argument(arg.name, help=arg.help, const=arg.default, nargs='?')
        else:
            parser.add_argument(arg.name, help=arg.help)


def create_account_sp(root):
    account_sp = root.add_parser('account', help='Account actions')
    account_sps = account_sp.add_subparsers()
    add_parser_with_func(
        account_sps, 'create', create_account, 'Create account'
    )
    add_parser_with_func(
        account_sps, 'import', import_account, 'Import account'
    )
    add_parser_with_args(
        account_sps, 'export', export_account, 'Export account',
        [ParserArgument('destination', 'Destination file', None)]
    )


def create_files_sp(root):
    files_sp = root.add_parser('files', help='Files actions')
    files_sps = files_sp.add_subparsers()
    add_parser_with_func(
        files_sps, 'list', list_files, 'List files'
    )
    add_parser_with_args(
        files_sps, 'upload', upload_file, 'Upload file',
        [ParserArgument('path', 'Path to a file', None)]
    )
    add_parser_with_args(
        files_sps, 'download', download_file, 'Download file',
        [ParserArgument('hash', 'Hash of a file', None),
         ParserArgument('destination', 'Destination', os.getcwd())]
    )
    add_parser_with_args(
        files_sps, 'info', get_file_info, 'Get file info',
        [ParserArgument('hash', 'Hash of a file', None)]
    )
    add_parser_with_args(
        files_sps, 'prolong_deposit', prolong_deposit, 'Prolong deposit for a file',
        [ParserArgument('hash', 'Hash of a file', None),
         ParserArgument('value', 'Deposit value (in MMR)', 0)]
    )


def create_user_sp(root):
    user_sp = root.add_parser('user', help='User info')
    user_sps = user_sp.add_subparsers()
    add_parser_with_func(
        user_sps, 'address', get_address, 'Get address'
    )
    add_parser_with_func(
        user_sps, 'role', get_role, 'Get role'
    )
    add_parser_with_func(
        user_sps, 'transactions', get_transactions, 'Get transactions'
    )
    add_parser_with_func(
        user_sps, 'balance', get_balance, 'Get balance'
    )


def create_host_sp(root):
    host_sp = root.add_parser('host', help='Host info')
    host_sps = host_sp.add_subparsers()
    add_parser_with_func(
        host_sps, 'status', get_host_status, 'Get host status'
    )
    add_parser_with_func(
        host_sps, 'ip', get_host_ip, 'Get host status'
    )
    storage_sp = host_sps.add_parser('storage', help='Storage info and actions')
    storage_sps = storage_sp.add_subparsers()
    add_parser_with_func(
        storage_sps, 'status', get_storage_info, 'Get storage info'
    )
    add_parser_with_args(
        storage_sps, 'resize', resize_storage, 'Resize storage',
        [ParserArgument('value', 'Value, GB', None)]
    )
    add_parser_with_args(
        storage_sps, 'set_path', set_box_dir, 'Set storage directory',
        [ParserArgument('path', 'New path to storage directory', None)]
    )


def create_miner_sp(root):
    miner_sp = root.add_parser('miner', help='Miner info')
    miner_sps = miner_sp.add_subparsers()
    add_parser_with_func(
        miner_sps, 'status', get_miner_status, 'Get miner status'
    )
    add_parser_with_func(
        miner_sps, 'ip', get_miner_ip, 'Get miner ip'
    )
    add_parser_with_func(
        miner_sps, 'request', miner_request, 'Send request for adding to a miner list'
    )


def parse_args():
    parser = argparse.ArgumentParser(description='Memority CLI')
    parser.add_argument('--memority_core_port', help='Daemon port', type=int, default=9379)
    root_sp = parser.add_subparsers()

    create_account_sp(root_sp)
    create_files_sp(root_sp)
    create_user_sp(root_sp)
    create_host_sp(root_sp)
    create_miner_sp(root_sp)

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(args.func(args))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
