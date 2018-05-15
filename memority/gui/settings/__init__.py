import os
import platform

import yaml

__all__ = ['settings']


def get_app_data_dir():
    __app_data_dir = {
        'Linux': lambda: os.path.join(os.getenv('HOME'), '.memority', 'ui'),
        'Windows': lambda: os.path.join(os.getenv('APPDATA'), 'Memority', 'ui'),
        'Darwin': lambda: os.path.join(os.getenv('HOME'), 'Library', 'Application Support', 'Memority UI')
    }.get(_platform_name, None)
    if not __app_data_dir:
        raise Exception(f'Unknown platform name: {_platform_name}')
    __path = __app_data_dir()
    if not os.path.exists(__path):
        os.makedirs(__path)
    return __path


class Settings:

    def __init__(self, data: dict) -> None:
        super().__setattr__('data', data)
        self.dump()

    def __setattr__(self, name: str, value) -> None:
        self.data[name] = value
        self.dump()

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError

    def __hasattr__(self, a):
        return a in self.data

    def dump(self):
        with open(self.local_settings_path, 'w') as outfile:
            yaml.dump(self.data, outfile, default_flow_style=False)

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
    def daemon_address(self):
        return f'127.0.0.1:{self.renter_app_port}'

    @classmethod
    def load(cls):
        with open(str(_default_settings_path), 'r') as defaults_file:
            default_s = yaml.load(defaults_file)

        if os.path.isfile(_local_settings_path):
            with open(_local_settings_path, 'r') as locals_file:
                local_s = yaml.load(locals_file)
        else:
            local_s = {}

        return Settings({
            **default_s,
            **local_s,  # overwrite defaults if different
        })

    @property
    def ui_dir(self):
        return os.path.join(_base_dir, 'ui')

    @property
    def ui_main_window(self):
        return os.path.join(self.ui_dir, 'main.ui')

    @property
    def ui_file_list_item(self):
        return os.path.join(self.ui_dir, 'file_list_item.ui')

    @property
    def ui_generate_address(self):
        return os.path.join(self.ui_dir, 'generate_address.ui')

    @property
    def ui_add_key(self):
        return os.path.join(self.ui_dir, 'add_key.ui')

    @property
    def ui_create_account(self):
        return os.path.join(self.ui_dir, 'create_account.ui')

    @property
    def ui_create_deposit_for_file(self):
        return os.path.join(self.ui_dir, 'create_deposit_for_file.ui')

    @property
    def ui_enter_password(self):
        return os.path.join(self.ui_dir, 'enter_password.ui')

    @property
    def ui_submit_exit(self):
        return os.path.join(self.ui_dir, 'submit_exit.ui')

    @property
    def ui_error_msg(self):
        return os.path.join(self.ui_dir, 'error_msg.ui')


_base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
_platform_name = platform.system()
_app_data_dir = get_app_data_dir()
_local_settings_path = os.path.join(_app_data_dir, "settings", "locals.yml")
_default_settings_path = os.path.join(_base_dir, "settings", "defaults.yml")

settings = Settings.load()
