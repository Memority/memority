import getpass
import os

from settings import settings
from .encryption import compute_hash, verify_signature, encrypt, decrypt, sign, InvalidSignature, DecryptionError
from .get_ip import get_ip, check_if_white_ip

__all__ = ['check_first_run', 'ask_for_password',
           'compute_hash', 'verify_signature', 'encrypt', 'decrypt', 'sign', 'InvalidSignature', 'DecryptionError',
           'get_ip']


def check_first_run():
    if os.path.isfile(settings.local_settings_secrets_path):
        return False
    return True


async def ask_for_password(_password, ask=False):
    if ask:
        _password = getpass.getpass()
    return _password
