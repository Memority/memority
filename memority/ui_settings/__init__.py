import os
import platform

__all__ = ['ui_settings']


class Settings:

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
    def ui_bulk_prolong_deposit(self):
        return os.path.join(self.ui_dir, 'bulk_prolong_deposit.ui')

    @property
    def ui_enter_password(self):
        return os.path.join(self.ui_dir, 'enter_password.ui')

    @property
    def ui_submit_exit(self):
        return os.path.join(self.ui_dir, 'submit_exit.ui')

    @property
    def ui_error_msg(self):
        return os.path.join(self.ui_dir, 'error_msg.ui')

    @property
    def ui_info_msg(self):
        return os.path.join(self.ui_dir, 'info_msg.ui')


_base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
_platform_name = platform.system()

ui_settings = Settings()
