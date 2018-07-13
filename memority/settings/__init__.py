import contextlib
import json
import os
import platform
import random
import shutil
import string
from shutil import copyfile

import ecdsa
import sha3
import yaml

__all__ = ['settings', 'Settings']


def get_app_data_dir():
    __app_data_dir = {
        'Linux': lambda: os.path.join(os.getenv('HOME'), '.memority', 'core'),
        'Windows': lambda: os.path.join(os.getenv('APPDATA'), 'Memority', 'core'),
        'Darwin': lambda: os.path.join(os.getenv('HOME'), 'Library', 'Application Support', 'Memority Core')
    }.get(_platform_name, None)
    if not __app_data_dir:
        raise Exception(f'Unknown platform name: {_platform_name}')
    __path = __app_data_dir()
    if not os.path.exists(__path):
        os.makedirs(__path, exist_ok=True)
    return __path


def get_user_home_dir():
    __user_home_dir = {
        'Linux': lambda: os.path.join(os.getenv('HOME')),
        'Windows': lambda: os.path.join(os.getenv('HOMEPATH')),
        'Darwin': lambda: os.path.join(os.getenv('HOME'))
    }.get(_platform_name, None)
    if not __user_home_dir:
        raise Exception(f'Unknown platform name: {_platform_name}')
    return __user_home_dir()


class Settings:
    class Locked(Exception):
        ...

    class InvalidPassword(Exception):
        ...

    def __init__(self) -> None:
        if not self.__hasattr__('boxes_dir'):
            path = os.path.join(_app_data_dir, 'boxes')
            if not os.path.exists(path):
                os.makedirs(path)
            self.boxes_dir = path

    def __setattr__(self, name: str, value) -> None:
        data = self.load()
        data[name] = value
        self.encrypt_secrets(data)

    def __getattr__(self, item):
        if item in [
            'encryption_key',
            'public_key',
            'private_key',
            'address',
            'client_contract_address',
            'client_contract_version'
        ] and os.path.isfile(self.local_settings_secrets_path):
            if not hasattr(self, 'password'):
                raise self.Locked
            if not self.password:
                raise self.Locked
            data = self.read_encrypted()
        elif item in [
            'version',
            'min_balance_for_mining'
        ]:
            data = self.load_defaults()
        else:
            data = self.load()
        try:
            return data[item]
        except KeyError:
            return None

    def __hasattr__(self, a):
        return (
                a in self.load() or (
                    a in [
                        'encryption_key',
                        'public_key',
                        'private_key',
                        'address',
                        'client_contract_address',
                        'client_contract_version'
                    ]
                    if os.path.isfile(self.local_settings_secrets_path)
                    else False
                )
        )

    def unlock(self, password):
        super().__setattr__('password', password)
        self.read_encrypted()
        self.encrypt_secrets(self.load())

    def change_password(self):
        ...  # ToDo: implement

    def dump(self, data=None):
        if not data:
            data = self.load()
            self.encrypt_secrets(data)
        else:
            with open(self.local_settings_path, 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

    def encrypt_secrets(self, data):
        data_to_enc = {}
        for key in ['encryption_key', 'public_key', 'private_key', 'address', 'client_contract_address',
                    'client_contract_version']:
            val = data.pop(key, None)
            if val:
                data_to_enc[key] = val
        if data_to_enc:
            self.dump_encrypted({
                **self.read_encrypted(),
                **data_to_enc
            })
        self.dump(data)

    def dump_encrypted(self, data: dict):
        if not hasattr(self, 'password'):
            raise self.Locked
        data = json.dumps(data)
        from utils import encrypt
        encrypted = encrypt(data.encode('utf-8'), password=self.password)
        with open(self.local_settings_secrets_path, 'wb') as outfile:
            outfile.write(encrypted)

    def read_encrypted(self):
        if not hasattr(self, 'password'):
            raise self.Locked
        if not os.path.isfile(self.local_settings_secrets_path):
            return {}
        with open(self.local_settings_secrets_path, 'rb') as f:
            data = f.read()
            if not data:
                return {}
        from utils import DecryptionError
        try:
            from utils import decrypt
            decrypted = decrypt(data, self.password)
            data = json.loads(decrypted)
            if 'client_contract_version' not in data:
                data['client_contract_version'] = 0
            return data
        except DecryptionError:
            raise self.InvalidPassword

    def generate_keys(self, password):
        self.unlock(password)
        copyfile(self.local_settings_path, f'{self.local_settings_path}.bak')
        with contextlib.suppress(FileNotFoundError):
            copyfile(self.local_settings_secrets_path, f'{self.local_settings_secrets_path}.bak')
        keccak = sha3.keccak_256()
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key().to_string()
        keccak.update(public_key)
        address = f'0x{keccak.hexdigest()[24:]}'
        seed = private_key.to_string().hex()
        num = self.key_len
        random.seed(seed)
        key = ''.join(random.choices(string.printable, k=num))
        self.dump_encrypted({
            'encryption_key': key,
            'public_key': public_key.hex(),
            'private_key': private_key.to_string().hex(),
            'address': address,
        })

    @staticmethod
    def load_defaults():
        with open(_default_settings_path, 'r') as defaults_file:
            default_s = yaml.load(defaults_file)
        return default_s

    @staticmethod
    def load_locals():
        if os.path.isfile(_local_settings_path):
            with open(_local_settings_path, 'r') as locals_file:
                local_s = yaml.load(locals_file)
        else:
            local_s = {}
        return local_s

    @classmethod
    def load(cls):
        return {
            **cls.load_defaults(),
            **cls.load_locals()  # overwrite defaults if different
        }

    @property
    def daemon_address(self):
        return f'127.0.0.1:{self.renter_app_port}'

    @property
    def log_dir(self):
        path = os.path.join(_app_data_dir, 'logs')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def db_path(self):
        return os.path.join(_app_data_dir, 'memority.db')

    @property
    def db_migrations_path(self):
        return os.path.join(_base_dir, 'models', 'db_migrations')

    @property
    def default_settings_path(self):
        return _default_settings_path

    @property
    def local_settings_path(self):
        if not os.path.isfile(_local_settings_path):
            local_settings_dir = os.path.normpath(os.path.join(_local_settings_path, os.pardir))
            if not os.path.exists(local_settings_dir):
                os.makedirs(local_settings_dir)
        return _local_settings_path

    @property
    def local_settings_secrets_path(self):
        return os.path.join(_app_data_dir, "settings", "secrets.bin")

    @property
    def blockchain_dir(self):
        return os.path.join(_app_data_dir, 'blockchain_db')

    @property
    def default_downloads_dir(self):
        return os.path.join(_user_home_dir, 'Downloads')

    @property
    def geth_executable(self):
        return os.path.join(_base_dir, 'geth', 'geth.exe' if _platform_name == 'Windows' else 'geth')

    @property
    def geth_init_json(self):
        return os.path.join(_base_dir, 'smart_contracts', 'install', 'mmr_chain_v1.json')

    @property
    def geth_static_nodes_json(self):
        return os.path.join(_base_dir, 'smart_contracts', 'install', 'static-nodes.json')

    @property
    def contract_sources_dir(self):
        return os.path.join(_base_dir, 'smart_contracts', 'contracts')

    @property
    def contract_binaries_dir(self):
        return os.path.join(_base_dir, 'smart_contracts', 'binaries')

    @property
    def base_dir(self):
        return _base_dir

    @property
    def contracts_json(self):
        return os.path.join(_base_dir, 'smart_contracts', 'contracts.json')

    def import_account(self, filename, password):
        # region Backup current account
        if os.path.isfile(self.local_settings_secrets_path):
            local_settings_backup_path = f'{self.local_settings_secrets_path}.bak'
            if os.path.isfile(local_settings_backup_path):
                i = 0
                while True:
                    _path = f'{local_settings_backup_path}.{i}'
                    if not os.path.isfile(_path):
                        local_settings_backup_path = _path
                        break
                    i += 1
            shutil.copyfile(
                os.path.join(self.local_settings_secrets_path),
                os.path.join(local_settings_backup_path)
            )
        # endregion
        # region Replace file
        shutil.copyfile(
            os.path.join(filename),
            os.path.join(self.local_settings_secrets_path)
        )
        # endregion
        self.unlock(password)
        from smart_contracts import import_private_key_to_eth
        import_private_key_to_eth(password, self.private_key)

    def export_account(self, filename):
        shutil.copyfile(
            os.path.join(self.local_settings_secrets_path),
            os.path.join(filename)
        )


_platform_name = platform.system()
_base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
_app_data_dir = get_app_data_dir()
_user_home_dir = get_user_home_dir()
_default_settings_path = os.path.join(_base_dir, "settings", "defaults.yml")
_local_settings_path = os.path.join(_app_data_dir, "settings", "locals.yml")

settings = Settings()
