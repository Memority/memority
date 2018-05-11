import sys

import asyncio
import os
from PyQt5.QtWidgets import *

from dialogs import ask_for_password
from handlers import error_handler, log
from utils import *


class HostingSettingsWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        self.disk_space_input = QSpinBox()
        self.disk_space_input.setMaximum(1024 ** 3)
        main_layout.addWidget(QLabel('Disk space for hosting, GB:'), 0, 0)
        main_layout.addWidget(self.disk_space_input, 0, 2)
        self.box_dir_input = QLineEdit()
        self.box_dir_input.setReadOnly(True)
        self.select_dir_btn = QPushButton('Change...')
        self.select_dir_btn.clicked.connect(self.change_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.box_dir_input)
        dir_layout.addWidget(self.select_dir_btn)
        main_layout.addWidget(QLabel('Directory to store files:'), 1, 0)
        main_layout.addLayout(dir_layout, 1, 2)
        main_layout.addItem(QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Fixed), 2, 1)

    def change_directory(self):
        directory = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            directory=os.getenv('HOME', None) or os.getenv('HOMEPATH', None),

        )
        if directory:
            self.box_dir_input.setText(directory)


class ControlButtonsWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.apply_btn = QPushButton('Apply')
        self.cancel_btn = QPushButton('Reset')

        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        main_layout.addWidget(self.apply_btn)
        main_layout.addItem(QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        main_layout.addWidget(self.cancel_btn)

    def enable(self):
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)


class TabSettingsWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.parent_widget = parent
        self.main_window = main_window
        self.session = main_window.session
        self.log_widget = main_window.log_widget
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.create_account_btn = QPushButton('Create account')
        self.import_account_btn = QPushButton('Import account')
        self.export_account_btn = QPushButton('Export account')
        self.hosting_settings = HostingSettingsWidget(self)
        self.become_a_hoster_btn = QPushButton('Become a hoster')
        self.control_buttons = ControlButtonsWidget(self)
        self.create_account_btn.clicked.connect(lambda: asyncio.ensure_future(self.create_account()))
        self.import_account_btn.clicked.connect(lambda: asyncio.ensure_future(self.import_account()))
        self.export_account_btn.clicked.connect(lambda: asyncio.ensure_future(self.export_account()))
        self.hosting_settings.disk_space_input.valueChanged.connect(self.control_buttons.enable)
        self.hosting_settings.box_dir_input.textChanged.connect(self.control_buttons.enable)
        self.become_a_hoster_btn.clicked.connect(lambda: asyncio.ensure_future(self.become_a_hoster()))
        self.control_buttons.apply_btn.clicked.connect(lambda: asyncio.ensure_future(self.apply()))
        self.control_buttons.cancel_btn.clicked.connect(lambda: asyncio.ensure_future(self.reset()))

        main_layout.addWidget(self.create_account_btn)
        main_layout.addWidget(self.import_account_btn)
        main_layout.addWidget(self.export_account_btn)
        main_layout.addWidget(self.hosting_settings)
        main_layout.addWidget(self.become_a_hoster_btn)
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        main_layout.addWidget(self.control_buttons)

        for el in [self.create_account_btn, self.import_account_btn,
                   self.export_account_btn, self.become_a_hoster_btn, self.hosting_settings]:
            el.hide()
        self.control_buttons.apply_btn.setDisabled(True)
        self.control_buttons.cancel_btn.setDisabled(True)

    def log(self, msg):
        return log(msg, self.log_widget)

    async def refresh(self):
        role = await get_user_role(self.session)
        disk_space_for_hosting = await get_disk_space_for_hosting(self.session)
        box_dir = await get_box_gir(self.session)
        self.hosting_settings.disk_space_input.setValue(disk_space_for_hosting)
        self.hosting_settings.box_dir_input.setText(box_dir)
        address = await get_address(session=self.session)

        for btn in [self.create_account_btn, self.import_account_btn,
                    self.export_account_btn, self.become_a_hoster_btn]:
            btn.hide()

        self.import_account_btn.show()
        if role:
            self.export_account_btn.show()
            if role in ['hoster', 'both']:
                self.hosting_settings.show()
                self.hosting_settings.show()
            elif role == 'client':
                self.become_a_hoster_btn.show()
        else:
            self.create_account_btn.show()
            if address:
                self.create_account_btn.show()

    async def create_account(self):
        password1, ok = ask_for_password('Set password for your wallet')
        if not ok:
            return
        password2, ok = ask_for_password('Confirm')
        if not ok:
            return
        if password1 != password2:
            error_handler('Password don`t match!')
            return
        self.log(f'Generating address...')
        address = await generate_address(password=password1, session=self.session)
        await self.main_window.refresh()
        self.log(f'Your address: {address}')
        key, ok = QInputDialog.getText(
            None,
            "Key input",
            "<a>Paste your Alpha Tester Key here.</a><br>"
            "<a>You can get it after registering on https://memority.io</a>"
        )
        self.log('Please wait while we’ll send you MMR tokens for testing, it may take a few minutes. '
                 'Do not close the application.')
        balance = await request_mmr(key=key, session=self.session)
        if not balance:
            return
        self.log(f'Done! Your balance: {balance} MMR')
        await self.main_window.refresh()
        items = {
            'Store my files': 'client',
            'Be a hoster': 'host',
            'Both': 'both'
        }
        item, ok = QInputDialog.getItem(
            None,
            "Select role",
            "I want to...",
            items.keys(),
            0, False)
        if not ok:
            return
        role = items.get(item)
        self.log(f'Creating account for role "{role}"...\n'
                 f'This can take up to 60 seconds, as transaction is being written in blockchain.')
        if role in ['client', 'both']:
            self.log('Creating client account. When finished, the "My Files" tab appears.')
            ok = await create_account(role='client', session=self.session)
            if not ok:
                return
            self.log('Client account successfully created!')
            await self.main_window.refresh()
        if role in ['hoster', 'both']:
            self.log('Creating hoster account. When finished, the "Hosting statistics" tab appears.')
            ok = await create_account(role='host', session=self.session)
            if not ok:
                return
            self.log('Hoster account successfully created!')
            await self.main_window.refresh()
        # QMessageBox.information(None, 'Info', 'Account successfully created!')
        await self.main_window.refresh()

    async def import_account(self):
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Select Directory",
            os.path.join(os.getenv('HOME', None) or os.getenv('HOMEPATH', None), 'memority_account.bin'),
            "*.bin"
        )
        if filename:
            self.log('Importing account...')
            ok = await import_account(filename, self.session)
            if ok:
                self.log(f'Successfully imported {filename}')
                while True:
                    password, ok = ask_for_password('Password to exported account:')
                    if not ok:
                        sys.exit()
                    if not unlock_account(password):
                        continue
                    break
        await self.main_window.refresh()

    async def export_account(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Select Directory",
            os.path.join(os.getenv('HOME', None) or os.getenv('HOMEPATH', None), 'memority_account.bin'),
            "*.bin"
        )
        if filename:
            self.log('Exporting account...')
            ok = await export_account(filename, self.session)
            if ok:
                self.log(f'Exported to {filename}')

    async def become_a_hoster(self):
        self.log('Adding your address and IP to contract...\n'
                 'This can take up to 60 seconds, as transaction is being written in blockchain.\n'
                 'When finished, the "Hosting statistics" tab appears.')
        ok = await create_account(role='host', session=self.session)
        if ok:
            self.log('Successfully added to hoster list!')
        await self.main_window.refresh()

    async def apply(self):
        disk_space = self.hosting_settings.disk_space_input.value()
        await set_disk_space_for_hosting(disk_space=disk_space, session=self.session)
        box_dir = self.hosting_settings.box_dir_input.text()
        await change_box_dir(box_dir=box_dir, session=self.session)

    async def reset(self):
        ...
