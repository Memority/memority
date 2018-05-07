import asyncio
from decimal import Decimal

from PyQt5.QtWidgets import *

from utils import get_address, get_balance, get_token_price


class InfoWidget(QWidget):

    def __init__(self, parent, main_window, parent_widget):
        super().__init__(parent)
        self.parent_widget = parent_widget
        self.session = main_window.session
        self.grid = QGridLayout(self)
        self.setLayout(self.grid)

        self.grid.addWidget(QLabel('Address:'), 0, 0)
        # self.addr_display = QLabel('')
        self.addr_display = QLineEdit()
        self.addr_display.setReadOnly(True)
        self.grid.addWidget(self.addr_display, 0, 1)

        self.grid.addWidget(QLabel('Balance:'), 1, 0)
        self.mmr_bal_display = QLabel('')
        self.grid.addWidget(self.mmr_bal_display, 1, 1)

        self.grid.addWidget(QLabel('MMR price:'), 2, 0)
        self.mmr_price_display = QLabel('')
        self.grid.addWidget(self.mmr_price_display, 2, 1)

        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.setFixedWidth(100)
        self.refresh_btn.clicked.connect(lambda: asyncio.ensure_future(main_window.refresh()))
        self.grid.addWidget(self.refresh_btn, 3, 0)
        asyncio.ensure_future(self.refresh())

    async def refresh(self):
        address = await get_address(self.session) or 'Please go to "Settings" - "Create account"'
        balance = await get_balance(self.session) or 0
        token_price = await get_token_price(self.session)
        bal_price = str(Decimal(Decimal(balance) * Decimal(token_price)).quantize(Decimal('.01')))
        self.addr_display.setText(address)
        self.mmr_bal_display.setText(f'{balance} MMR (~{bal_price} USD)')
        self.mmr_price_display.setText(f'1 MMR = {token_price} USD')
        await self.parent_widget.refresh()


class ControlsWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)


class TabWalletWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.info_widget = InfoWidget(self, main_window, parent)
        self.controls_widget = ControlsWidget(self, main_window)
        self.layout.addWidget(self.info_widget)
        self.layout.addItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.layout.addWidget(self.controls_widget)
        self.setLayout(self.layout)
