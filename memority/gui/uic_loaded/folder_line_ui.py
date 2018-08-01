# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'folder_line.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(841, 70)
        Form.setStyleSheet("QWidget{\n"
"background: #fff;\n"
"border: 2px solid #eee;\n"
"}")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setStyleSheet("border: none;")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.file_name = QtWidgets.QTextBrowser(Form)
        self.file_name.setMinimumSize(QtCore.QSize(0, 4))
        self.file_name.setMaximumSize(QtCore.QSize(250, 500))
        self.file_name.setStyleSheet("border: none;\n"
"color: #7d7d7d;")
        self.file_name.setObjectName("file_name")
        self.horizontalLayout.addWidget(self.file_name)
        self.file_size = QtWidgets.QTextBrowser(Form)
        self.file_size.setMinimumSize(QtCore.QSize(0, 4))
        self.file_size.setStyleSheet("border: none;")
        self.file_size.setObjectName("file_size")
        self.horizontalLayout.addWidget(self.file_size)
        self.upload_date = QtWidgets.QTextBrowser(Form)
        self.upload_date.setMinimumSize(QtCore.QSize(0, 4))
        self.upload_date.setStyleSheet("border: none;")
        self.upload_date.setObjectName("upload_date")
        self.horizontalLayout.addWidget(self.upload_date)
        self.textBrowser_4 = QtWidgets.QTextBrowser(Form)
        self.textBrowser_4.setMinimumSize(QtCore.QSize(0, 4))
        self.textBrowser_4.setStyleSheet("border: none;")
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.horizontalLayout.addWidget(self.textBrowser_4)
        self.download_btn = QtWidgets.QLabel(Form)
        self.download_btn.setMinimumSize(QtCore.QSize(40, 0))
        self.download_btn.setStyleSheet("border: none;")
        self.download_btn.setObjectName("download_btn")
        self.horizontalLayout.addWidget(self.download_btn)
        self.prolong_btn = QtWidgets.QPushButton(Form)
        self.prolong_btn.setMinimumSize(QtCore.QSize(140, 36))
        self.prolong_btn.setStyleSheet("font-size: 16px;\n"
"color: #757575;\n"
"border: 1px solid #757575;\n"
"border-radius: 7px;")
        self.prolong_btn.setObjectName("prolong_btn")
        self.horizontalLayout.addWidget(self.prolong_btn)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p align=\"center\"><img src=\":/folder/folder.png\"/></p></body></html>"))
        self.file_name.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">My document</span></p></body></html>"))
        self.file_size.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#7d7d7d;\">1GB</span></p></body></html>"))
        self.upload_date.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#7d7d7d;\">26.04.2018</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#7d7d7d;\">08:33 UTC</span></p></body></html>"))
        self.textBrowser_4.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#7d7d7d;\">26.04.2019</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#7d7d7d;\">08:33 UTC</span></p></body></html>"))
        self.download_btn.setText(_translate("Form", "<html><head/><body><p align=\"center\"><img src=\":/download/download.png\"/></p></body></html>"))
        self.prolong_btn.setText(_translate("Form", "Prolong deposit"))

import download_rc
import folder_rc
