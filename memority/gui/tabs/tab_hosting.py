import asyncio

from PyQt5.QtWidgets import *

from utils import get_address, get_host_ip, get_space_used


class TabHostingWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.session = main_window.session
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(QLabel('Address:'), 0, 0)
        self.grid_layout.addWidget(QLabel('IP:'), 1, 0)  # ToDo: warn if not accessible
        self.grid_layout.addWidget(QLabel('Space used:'), 2, 0)
        self.address_display = QLabel('')
        self.ip_display = QLabel('')
        self.space_display = QLabel('')
        self.grid_layout.addWidget(self.address_display, 0, 1)
        self.grid_layout.addWidget(self.ip_display, 1, 1)
        self.grid_layout.addWidget(self.space_display, 2, 1)
        self.grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 2)
        self.layout.addLayout(self.grid_layout)
        self.layout.addWidget(QLabel('Payment for stored files is charged automatically once a week.'))
        asyncio.ensure_future(self.refresh())

    async def refresh(self):
        address = await get_address(self.session)
        ip = await get_host_ip(self.session) or 'Not in host list.'
        space_used = await get_space_used(self.session)
        self.address_display.setText(address)
        self.ip_display.setText(ip)
        self.space_display.setText(space_used)
