# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1025, 680)
        Form.setStyleSheet("background: #fff;\n"
"")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.about_mmr = QtWidgets.QVBoxLayout()
        self.about_mmr.setContentsMargins(45, 15, 45, 15)
        self.about_mmr.setSpacing(15)
        self.about_mmr.setObjectName("about_mmr")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.about_mmr.addItem(spacerItem1)
        self.logo = QtWidgets.QLabel(Form)
        self.logo.setObjectName("logo")
        self.about_mmr.addWidget(self.logo)
        self.text = QtWidgets.QTextBrowser(Form)
        self.text.setMinimumSize(QtCore.QSize(0, 200))
        self.text.setStyleSheet("border: none;")
        self.text.setObjectName("text")
        self.about_mmr.addWidget(self.text)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.about_mmr.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.about_mmr)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(20, -1, 50, -1)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem3 = QtWidgets.QSpacerItem(20, 655, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.title = QtWidgets.QLabel(Form)
        self.title.setMinimumSize(QtCore.QSize(0, 40))
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 70))
        self.lineEdit.setStyleSheet("border: 2px solid #bdbdbd;\n"
"border-radius: 10px;\n"
"background-color: rgba(255,255,255, 0);\n"
"background-image: url(:/key_main/key.png);\n"
"background-position: left 10px;\n"
"background-repeat: no-repeat;\n"
"padding: 0 15px 0px 55px;\n"
"font-size: 18px;")
        self.lineEdit.setText("")
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.create_acc = QtWidgets.QPushButton(Form)
        self.create_acc.setMinimumSize(QtCore.QSize(380, 0))
        self.create_acc.setStyleSheet("font-size: 20px;\n"
"background: #eeeeee;\n"
"border-radius: 7px;\n"
"padding: 20px;\n"
"color: #7a7a7a;")
        self.create_acc.setObjectName("create_acc")
        self.verticalLayout.addWidget(self.create_acc)
        self.or = QtWidgets.QHBoxLayout()
        self.or.setObjectName("or")
        self.line = QtWidgets.QFrame(Form)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("")
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.or.addWidget(self.line)
        self.textEdit_2 = QtWidgets.QTextEdit(Form)
        self.textEdit_2.setEnabled(False)
        self.textEdit_2.setMinimumSize(QtCore.QSize(0, 57))
        self.textEdit_2.setMaximumSize(QtCore.QSize(40, 35))
        self.textEdit_2.setStyleSheet("text-align: center;\n"
"font-size: 20px;\n"
"border: none;")
        self.textEdit_2.setObjectName("textEdit_2")
        self.or.addWidget(self.textEdit_2)
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.or.addWidget(self.line_2)
        self.verticalLayout.addLayout(self.or)
        self.loginButton = QtWidgets.QPushButton(Form)
        self.loginButton.setMinimumSize(QtCore.QSize(380, 0))
        self.loginButton.setStyleSheet("font-size: 20px;\n"
"background: #eeeeee;\n"
"border-radius: 7px;\n"
"padding: 20px;\n"
"color: #7a7a7a;")
        self.loginButton.setObjectName("loginButton")
        self.verticalLayout.addWidget(self.loginButton)
        self.import_2 = QtWidgets.QPushButton(Form)
        self.import_2.setMinimumSize(QtCore.QSize(380, 0))
        self.import_2.setStyleSheet("font-size: 20px;\n"
"background: #eeeeee;\n"
"border-radius: 7px;\n"
"padding: 20px;\n"
"color: #7a7a7a;")
        self.import_2.setObjectName("import_2")
        self.verticalLayout.addWidget(self.import_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 655, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.logo.setText(_translate("Form", "<html><head/><body><p><img src=\":/logo_main/logo.png\"/></p></body></html>"))
        self.text.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Source Sans Pro,sans-serif\'; font-size:12pt; color:#9e9e9e; background-color:#ffffff;\">Memority is the platform for a completely decentralized, ultra-secure storage of valuable data.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Source Sans Pro,sans-serif\'; font-size:12pt; color:#9e9e9e;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Source Sans Pro,sans-serif\'; font-size:12pt; color:#9e9e9e; background-color:#ffffff;\">On the blockchain, which ensures the continued availability of several encrypted copies of data on unrelated storage locations around the world.</span></p></body></html>"))
        self.title.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:14pt;\">Sign in</span></p></body></html>"))
        self.lineEdit.setPlaceholderText(_translate("Form", "Password"))
        self.create_acc.setText(_translate("Form", "Create Memority account"))
        self.textEdit_2.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:20px; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; color:#bdbdbd;\">or</span></p></body></html>"))
        self.loginButton.setText(_translate("Form", "Login"))
        self.import_2.setText(_translate("Form", "Import Account"))

from .resources.key_main_rc import *
from .resources.logo_main_rc import *
