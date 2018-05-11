import asyncio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from dialogs import ask_for_password


def log(msg, log_widget: QPlainTextEdit):
    log_widget.appendPlainText(msg)
    log_widget.moveCursor(QTextCursor.End)


def uploaded_file_handler(data, window):
    file_data = data.get('data').get('file')
    window.add_file_list_item(**file_data)
    log(f'Your file successfully uploaded! Hash: {file_data.get("hash")}', window.log_widget)
    QMessageBox.information(None, 'Success!', f'Your file successfully uploaded! Hash: {file_data.get("hash")}')


def downloaded_file_handler(data, window):
    file_data = data.get('data').get('file')
    log(f'Your file successfully downloaded! Path: {file_data.get("name")}', window.log_widget)
    QMessageBox.information(None, 'Success!', f'Your file successfully downloaded! Path: {file_data.get("name")}')


def file_list_handler(data, window):
    file_list = data.get('data').get('files')
    window.cleanup_file_list()
    for file in file_list:
        window.add_file_list_item(**file)


def error_handler(message_data, window=None):
    message = message_data.get('message') if isinstance(message_data, dict) else message_data
    if 'insufficient funds' in message:
        message = 'Error\n' \
                  'Account cannot be created without MMR tokens.'
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error")
    msg.setInformativeText(message)
    msg.setWindowTitle("Error")
    msg.exec()


def action_handler(message_data, window):
    action = message_data.get('details')
    if action == 'ask_for_password':
        password, ok = ask_for_password(message_data.get('message'))
        asyncio.ensure_future(window.ws_send({"status": "success", "password": password}))
    else:
        message = message_data.get('message')
        type_ = message_data.get('type')
        if type_ == 'bool':
            reply = QMessageBox().question(
                None,
                message,
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            result = True if reply == QMessageBox.Yes else False
        elif type_ == 'float':
            d = QDialog()
            vl = QVBoxLayout()
            d.setLayout(vl)
            lb = QLabel(message)
            lb.setTextInteractionFlags(Qt.TextSelectableByMouse)
            vl.addWidget(lb)
            sb = QDoubleSpinBox()
            sb.setValue(1)
            sb.setMinimum(1e-18)
            sb.setMaximum(1000)
            sb.setDecimals(18)
            vl.addWidget(sb)
            hl = QHBoxLayout()
            btn_ok = QPushButton('Ok')
            btn_ok.clicked.connect(d.reject)
            btn_c = QPushButton('Cancel')
            btn_c.clicked.connect(d.accept)
            hl.addWidget(btn_ok)
            hl.addWidget(btn_c)
            vl.addLayout(hl)
            ok = d.exec_()
            if ok:
                result = sb.value()
            else:
                result = -1
        else:
            result, ok = QInputDialog.getText(None, "", message)
            if not ok:
                return
        asyncio.ensure_future(window.ws_send({'status': 'success', 'result': result}))


def info_handler(message_data, window):
    log(
        message_data.get('message'),
        window.log_widget,
    )


WS_MESSAGE_HANDLERS = {
    "uploaded": uploaded_file_handler,
    "downloaded": downloaded_file_handler,
    "file_list": file_list_handler,
    "info": info_handler,
}


def process_ws_message(message_data: dict, window):
    status = message_data.get('status')
    if status == 'success':
        handler = WS_MESSAGE_HANDLERS.get(message_data.get('details'))
    elif status == 'action_needed':
        handler = action_handler
    else:
        handler = error_handler
    if handler:
        return handler(message_data, window)
