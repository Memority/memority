import os

from settings import settings
from .encryption import compute_hash, verify_signature, encrypt, decrypt, sign, InvalidSignature, DecryptionError
from .get_ip import get_ip, check_if_accessible

__all__ = ['check_first_run',
           'compute_hash', 'verify_signature', 'encrypt', 'decrypt', 'sign', 'InvalidSignature', 'DecryptionError',
           'get_ip', 'check_if_accessible']


def check_first_run():
    if os.path.isfile(settings.local_settings_secrets_path):
        return False
    return True
