# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'current_files.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(854, 331)
        Form.setStyleSheet("background: #fff;")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.prolong_btn = QtWidgets.QPushButton(Form)
        self.prolong_btn.setMinimumSize(QtCore.QSize(230, 45))
        self.prolong_btn.setStyleSheet("font-size: 16px;\n"
"color: #757575;\n"
"border-radius: 7px;\n"
"background: #eee;")
        self.prolong_btn.setObjectName("prolong_btn")
        self.horizontalLayout.addWidget(self.prolong_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.file_size = QtWidgets.QTextBrowser(Form)
        self.file_size.setMinimumSize(QtCore.QSize(0, 4))
        self.file_size.setMaximumSize(QtCore.QSize(16777215, 30))
        self.file_size.setStyleSheet("border: none;")
        self.file_size.setObjectName("file_size")
        self.horizontalLayout_3.addWidget(self.file_size)
        self.file_name = QtWidgets.QTextBrowser(Form)
        self.file_name.setMinimumSize(QtCore.QSize(0, 4))
        self.file_name.setMaximumSize(QtCore.QSize(250, 30))
        self.file_name.setStyleSheet("border: none;\n"
"color: #7d7d7d;")
        self.file_name.setObjectName("file_name")
        self.horizontalLayout_3.addWidget(self.file_name)
        self.upload_date = QtWidgets.QTextBrowser(Form)
        self.upload_date.setMinimumSize(QtCore.QSize(0, 4))
        self.upload_date.setMaximumSize(QtCore.QSize(16777215, 30))
        self.upload_date.setStyleSheet("border: none;")
        self.upload_date.setObjectName("upload_date")
        self.horizontalLayout_3.addWidget(self.upload_date)
        self.textBrowser_4 = QtWidgets.QTextBrowser(Form)
        self.textBrowser_4.setMinimumSize(QtCore.QSize(0, 4))
        self.textBrowser_4.setMaximumSize(QtCore.QSize(16777215, 30))
        self.textBrowser_4.setStyleSheet("border: none;")
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.horizontalLayout_3.addWidget(self.textBrowser_4)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setStyleSheet("border: none;")
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.textBrowser_5 = QtWidgets.QTextBrowser(Form)
        self.textBrowser_5.setMinimumSize(QtCore.QSize(0, 4))
        self.textBrowser_5.setMaximumSize(QtCore.QSize(16777215, 30))
        self.textBrowser_5.setStyleSheet("border: none;")
        self.textBrowser_5.setObjectName("textBrowser_5")
        self.horizontalLayout_3.addWidget(self.textBrowser_5)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.fo_files_2 = QtWidgets.QVBoxLayout()
        self.fo_files_2.setObjectName("fo_files_2")
        self.verticalLayout.addLayout(self.fo_files_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.prolong_btn_2 = QtWidgets.QPushButton(Form)
        self.prolong_btn_2.setMinimumSize(QtCore.QSize(53, 20))
        self.prolong_btn_2.setMaximumSize(QtCore.QSize(40, 16777215))
        self.prolong_btn_2.setStyleSheet("font-size: 16px;")
        self.prolong_btn_2.setObjectName("prolong_btn_2")
        self.horizontalLayout_2.addWidget(self.prolong_btn_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.fo_files = QtWidgets.QVBoxLayout()
        self.fo_files.setObjectName("fo_files")
        self.verticalLayout.addLayout(self.fo_files)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.label.raise_()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">Current files</span></p></body></html>"))
        self.label_2.setText(_translate("Form", "<html><head/><body><p><img src=\":/search/search.png\"/></p></body></html>"))
        self.prolong_btn.setText(_translate("Form", "Prolong deposit for all files"))
        self.file_size.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Size</p></body></html>"))
        self.file_name.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Name</p></body></html>"))
        self.upload_date.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Upload date</p></body></html>"))
        self.textBrowser_4.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Deposit ends</p></body></html>"))
        self.label_4.setText(_translate("Form", "<html><head/><body><p align=\"center\"><br/></p></body></html>"))
        self.textBrowser_5.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Option</p></body></html>"))
        self.label_3.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">Archive</span></p></body></html>"))
        self.prolong_btn_2.setText(_translate("Form", "Hide"))

from .resources.file_rc import *
from .resources.search_rc import *
