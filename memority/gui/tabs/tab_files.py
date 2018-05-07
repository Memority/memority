import os

from PyQt5.QtWidgets import *


class FileListItemHeader(QWidget):

    def __init__(self, parent, timestamp, status):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        header_time = QLabel(timestamp)
        header_status = QLabel(status)
        main_layout.addWidget(header_time)
        main_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))
        main_layout.addWidget(header_status)


class FileListItemRow(QWidget):

    def __init__(self, parent, name, hash_, deposit_ends_on):
        super().__init__(parent)
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        main_layout.addWidget(QLabel('Name:'), 0, 0)
        main_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Fixed, QSizePolicy.Fixed), 0, 1)
        main_layout.addWidget(QLabel(name), 0, 2)
        main_layout.addWidget(QLabel('Hash:'), 1, 0)
        main_layout.addWidget(QLabel(hash_), 1, 2)
        main_layout.addWidget(QLabel('Deposit ends on:'), 2, 0)
        deolabel = QLabel(deposit_ends_on)
        deolabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addWidget(deolabel, 2, 2)


class FileListItemButtons(QWidget):

    def __init__(self, parent, hash_, signature, main_window):
        super().__init__(parent)
        self.main_window = main_window
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        download_button = QPushButton('Download')
        prolong_deposit_button = QPushButton('Prolong deposit')
        prolong_deposit_button.clicked.connect(self.deposit_dialog)
        download_button.clicked.connect(self.download_file_dialog)
        prolong_deposit_button.setFixedWidth(150)
        main_layout.addWidget(download_button)
        main_layout.addWidget(prolong_deposit_button)
        self.hash = hash_
        self.signature = signature

    def deposit_dialog(self):
        dialog = QDialog(self)
        dialog.resize(512, 200)
        main_layout = QVBoxLayout(self)
        dialog.setLayout(main_layout)
        hash_e_label = QLabel('Hash of a file:')
        signature_label = QLabel('Signature:')
        textarea_h_e = QTextBrowser(dialog)
        textarea_h_e.setText(self.hash)
        textarea_sign = QTextBrowser(dialog)
        textarea_sign.setText(self.signature)
        main_layout.addWidget(hash_e_label)
        main_layout.addWidget(textarea_h_e)
        main_layout.addWidget(signature_label)
        main_layout.addWidget(textarea_sign)
        main_layout.addWidget(QLabel('---under construction---'))
        main_layout.addWidget(QLabel('Deposit'))
        main_layout.addWidget(QLabel('---under construction---'))
        dialog.exec_()

    def download_file_dialog(self):
        directory = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            directory=os.getenv('HOME', None) or os.getenv('HOMEPATH', None),

        )
        if directory:
            self.main_window.download_file(path=directory, hash_=self.hash)


class FileListItemPanel(QWidget):

    def __init__(self, parent, widgets):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        for widget in widgets:
            main_layout.addWidget(widget)


class FileListItemWidget(QWidget):

    def __init__(self, parent, hash_, signature, name, timestamp, status, deposit_ends_on, main_window):
        super().__init__(parent)
        self.setMaximumHeight(200)
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        main_layout.addWidget(frame)
        frame_layout = QHBoxLayout(frame)
        frame.setLayout(frame_layout)

        left_panel = FileListItemPanel(self, widgets=[
            FileListItemHeader(self, timestamp, status),
            FileListItemRow(self, name, hash_, deposit_ends_on)
        ])
        right_panel = FileListItemPanel(self, widgets=[
            FileListItemButtons(self, hash_, signature, main_window=main_window)
        ])
        frame_layout.addWidget(left_panel)
        frame_layout.addWidget(right_panel)


class FileListWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.items = []
        self.list_box = QVBoxLayout(self)
        self.setLayout(self.list_box)
        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content.setLayout(self.content_layout)

        scroll = QScrollArea()
        scroll.setWidget(self.content)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(800)
        self.list_box.addWidget(scroll)
        self.spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def cleanup_file_list(self):
        for i in self.items:
            self.content_layout.removeWidget(i)
        self.items = []
        self.content_layout.addItem(self.spacer)

    def add_item(self, hash, signature, name: str, timestamp, status, deposit_ends_on, **kwargs):  # noqa
        item = FileListItemWidget(self.content, hash, signature, name, timestamp, status, deposit_ends_on,
                                  main_window=self.main_window)
        self.items.append(item)
        self.content_layout.removeItem(self.spacer)
        self.content_layout.addWidget(item)
        self.content_layout.addItem(self.spacer)


class FileControlsWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.uploadButton = QPushButton("Upload file")
        self.prolongDepositButton = QPushButton("Prolong the deposit for all files")
        self.prolongDepositButton.hide()
        self.layout.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.uploadButton)
        self.layout.addWidget(self.prolongDepositButton)
        self.setLayout(self.layout)


class TabFilesWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.controls_widget = FileControlsWidget(self)
        self.files_list_widget = FileListWidget(self, main_window=main_window)
        self.layout.addWidget(self.controls_widget)
        self.layout.addWidget(self.files_list_widget)
        self.setLayout(self.layout)
