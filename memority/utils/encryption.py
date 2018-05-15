import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from ecdsa import SigningKey, SECP256k1, BadSignatureError, VerifyingKey

from settings import settings

__all__ = ["encrypt", "decrypt", "compute_hash", "sign", "verify_signature", "InvalidSignature", "DecryptionError"]


class InvalidSignature(Exception):
    ...


class DecryptionError(Exception):
    ...


def sign(data: bytes):
    sk = SigningKey.from_string(bytes.fromhex(settings.private_key), curve=SECP256k1)
    signature = sk.sign(data)
    return signature.hex()


def verify_signature(data: bytes, signature: str, public_key: str):
    vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)
    try:
        return vk.verify(bytes.fromhex(signature), data)
    except BadSignatureError:
        return False


def get_encryption_key(password=None):
    """
    Generate encryption key using a seed
    :return: urlsafe encoded key
    """
    if password:
        if len(password) < 32:
            password = f'{password}{"0"*(32-len(password))}'
        elif len(password) > 32:
            password = password[:32]
        return base64.urlsafe_b64encode(bytes(password, 'utf-8'))
    else:
        return base64.urlsafe_b64encode(bytes(settings.encryption_key, 'utf-8'))


def encrypt(data, password=None):
    """
    Symmetric encryption with key (Fernet)
    :param data: <bytes> data to encrypt
    :return: <bytes>
    """
    fernet = Fernet(get_encryption_key(password))
    cipher_text = fernet.encrypt(data)
    return cipher_text


def decrypt(cipher_text, password=None):
    """
    Decryption of Fernet-encrypted data
    :param cipher_text: <bytes>
    :return: <bytes>
    """
    fernet = Fernet(get_encryption_key(password))
    try:
        data = fernet.decrypt(cipher_text)
    except InvalidToken as err:
        raise DecryptionError(str(err))
    return data


def compute_hash(data) -> str:
    return hashlib.md5(data).hexdigest()
