#! /usr/bin/env python

import argparse
import asyncio

from cli import *


def parse_args():
    parser = argparse.ArgumentParser(description='Memority CLI')
    parser.add_argument('--memority_core_port', help='Daemon port', type=int, default=9379)
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list_files', help='List files')
    parser_list.set_defaults(func=list_files)

    parser_list = subparsers.add_parser('create_account', help='Create account')
    parser_list.set_defaults(func=create_account)

    parser_list = subparsers.add_parser('become_a_hoster', help='Become a hoster')
    parser_list.set_defaults(func=become_a_hoster)

    parser_list = subparsers.add_parser('get_address', help='Get address')
    parser_list.set_defaults(func=get_address)

    parser_list = subparsers.add_parser('get_balance', help='Get balance')
    parser_list.set_defaults(func=get_balance)

    parser_upload = subparsers.add_parser('upload', help='Upload file')
    parser_upload.add_argument('path', help='Path to file')
    parser_upload.set_defaults(func=upload_file)

    parser_download = subparsers.add_parser('download', help='Download file')
    parser_download.add_argument('hash', help='Hash of file')
    parser_download.add_argument('destination', help='Destination')
    parser_download.set_defaults(func=download_file)

    parser_list = subparsers.add_parser('miner_request', help='Send request for adding to a miner list')
    parser_list.set_defaults(func=miner_request)

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
