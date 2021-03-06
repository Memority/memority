import os

from settings import settings
from .encryption import compute_hash, verify_signature, encrypt, decrypt, sign, InvalidSignature, DecryptionError
from .get_ip import get_ip, check_if_accessible

__all__ = ['check_first_run',
           'compute_hash', 'verify_signature', 'encrypt', 'decrypt', 'sign', 'InvalidSignature', 'DecryptionError',
           'get_ip', 'check_if_accessible', 'file_size_human_readable']


def check_first_run():
    if os.path.isfile(settings.local_settings_secrets_path):
        return False
    return True


def file_size_human_readable(size):
    if size < 1024:
        size = f'{size} B'
    elif size < 1024 ** 2:
        size = f'{size / 1024:.2f} KB'
    elif size < 1024 ** 3:
        size = f'{size / 1024 ** 2:.2f} MB'
    else:
        size = f'{size / 1024 ** 3:.2f} GB'
    return size
