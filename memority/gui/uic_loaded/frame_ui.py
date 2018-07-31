# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frame.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1070, 679)
        Form.setStyleSheet("QWidget{\n"
"background: #fff;\n"
"}\n"
"QGroupBox#balance QLabel{\n"
"font-size: 14px;\n"
"}\n"
"QGroupBox#balance QGroupBox{\n"
"border: none;\n"
"}\n"
"QGroupBox#profile{\n"
"background-image: url(:/profile/profile.png);\n"
"background-position: 0 0;\n"
"}\n"
"QPushButton#upload{\n"
"background: #fff;\n"
"}")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 100))
        self.groupBox.setStyleSheet("background: #eee;\n"
"border: none;")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.balance = QtWidgets.QGroupBox(self.groupBox)
        self.balance.setTitle("")
        self.balance.setObjectName("balance")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.balance)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.EMT_balance = QtWidgets.QGroupBox(self.balance)
        self.EMT_balance.setTitle("")
        self.EMT_balance.setObjectName("EMT_balance")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.EMT_balance)
        self.verticalLayout.setObjectName("verticalLayout")
        self.crypto_name = QtWidgets.QLabel(self.EMT_balance)
        self.crypto_name.setMinimumSize(QtCore.QSize(0, 20))
        self.crypto_name.setObjectName("crypto_name")
        self.verticalLayout.addWidget(self.crypto_name)
        self.crypto_amount = QtWidgets.QLabel(self.EMT_balance)
        self.crypto_amount.setMinimumSize(QtCore.QSize(0, 20))
        self.crypto_amount.setObjectName("crypto_amount")
        self.verticalLayout.addWidget(self.crypto_amount)
        self.horizontalLayout.addWidget(self.EMT_balance)
        self.MMR_balance = QtWidgets.QGroupBox(self.balance)
        self.MMR_balance.setTitle("")
        self.MMR_balance.setObjectName("MMR_balance")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.MMR_balance)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.crypto_name_2 = QtWidgets.QLabel(self.MMR_balance)
        self.crypto_name_2.setMinimumSize(QtCore.QSize(0, 20))
        self.crypto_name_2.setObjectName("crypto_name_2")
        self.verticalLayout_2.addWidget(self.crypto_name_2)
        self.crypto_amount_2 = QtWidgets.QLabel(self.MMR_balance)
        self.crypto_amount_2.setMinimumSize(QtCore.QSize(0, 20))
        self.crypto_amount_2.setObjectName("crypto_amount_2")
        self.verticalLayout_2.addWidget(self.crypto_amount_2)
        self.horizontalLayout.addWidget(self.MMR_balance)
        self.horizontalLayout_3.addWidget(self.balance)
        self.profile = QtWidgets.QGroupBox(self.groupBox)
        self.profile.setMinimumSize(QtCore.QSize(190, 0))
        self.profile.setStyleSheet("background-image: url(:/profile/profile.png);\n"
"background-position:left;\n"
"background-repeat: no-repeat;\n"
"background-size: 50px;\n"
"background-size: cover;")
        self.profile.setTitle("")
        self.profile.setObjectName("profile")
        self.label_2 = QtWidgets.QLabel(self.profile)
        self.label_2.setGeometry(QtCore.QRect(70, 20, 91, 16))
        self.label_2.setStyleSheet("background: none;")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.profile)
        self.label_3.setGeometry(QtCore.QRect(70, 40, 71, 20))
        self.label_3.setMinimumSize(QtCore.QSize(0, 20))
        self.label_3.setStyleSheet("background: none;\n"
"background-image: url(:/angle/angle_grey.png);\n"
"background-position: right;\n"
"background-repeat: no-repeat;")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.profile)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_3.setMinimumSize(QtCore.QSize(250, 0))
        self.groupBox_3.setMaximumSize(QtCore.QSize(250, 16777215))
        self.groupBox_3.setStyleSheet("background: #bdbdbd;")
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setContentsMargins(0, 20, 0, 11)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.upload = QtWidgets.QPushButton(self.groupBox_3)
        self.upload.setStyleSheet("background: #fff;\n"
"font-size: 16px;\n"
"color: #374356;\n"
"padding: 15px;\n"
"border: none;\n"
"border-radius: 7px;\n"
"font-weight: bold;\n"
"margin-left: 25px;\n"
"margin-right: 25px;")
        self.upload.setObjectName("upload")
        self.verticalLayout_4.addWidget(self.upload)
        self.menu = QtWidgets.QVBoxLayout()
        self.menu.setContentsMargins(-1, 15, -1, -1)
        self.menu.setObjectName("menu")
        self.data_owner_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.data_owner_btn.setStyleSheet("padding: 15px;\n"
"color: #fff;\n"
"font-size: 16px;\n"
"background: #9e9e9e;\n"
"border: none;\n"
"text-align: left;\n"
"padding-left:65px;\n"
"background-image: url(:/w_1/1_w.png);\n"
"background-position: center left;\n"
"background-repeat: no-repeat;")
        self.data_owner_btn.setObjectName("data_owner_btn")
        self.menu.addWidget(self.data_owner_btn)
        self.hoster_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.hoster_btn.setStyleSheet("padding: 15px;\n"
"font-size: 16px;\n"
"background: none;\n"
"border: none;\n"
"text-align: left;\n"
"padding-left:65px;\n"
"background-image: url(:/2_g/2_g.png);\n"
"background-position: center left;\n"
"background-repeat: no-repeat;")
        self.hoster_btn.setObjectName("hoster_btn")
        self.menu.addWidget(self.hoster_btn)
        self.wallet_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.wallet_btn.setStyleSheet("padding: 15px;\n"
"font-size: 16px;\n"
"background: none;\n"
"border: none;\n"
"text-align: left;\n"
"padding-left:65px;\n"
"background-image: url(:/3_g/3_g.png);\n"
"background-position: center left;\n"
"background-repeat: no-repeat;")
        self.wallet_btn.setObjectName("wallet_btn")
        self.menu.addWidget(self.wallet_btn)
        self.miner_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.miner_btn.setStyleSheet("padding: 15px;\n"
"font-size: 16px;\n"
"background: none;\n"
"border: none;\n"
"text-align: left;\n"
"padding-left:65px;\n"
"background-image: url(:/4_g/4_g.png);\n"
"background-position: center left;\n"
"background-repeat: no-repeat;")
        self.miner_btn.setObjectName("miner_btn")
        self.menu.addWidget(self.miner_btn)
        self.settings_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.settings_btn.setStyleSheet("padding: 15px;\n"
"font-size: 16px;\n"
"background: none;\n"
"border: none;\n"
"text-align: left;\n"
"padding-left:65px;\n"
"background-image: url(:/5_g/5_g.png);\n"
"background-position: center left;\n"
"background-repeat: no-repeat;")
        self.settings_btn.setObjectName("settings_btn")
        self.menu.addWidget(self.settings_btn)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.menu.addItem(spacerItem1)
        self.verticalLayout_4.addLayout(self.menu)
        self.horizontalLayout_2.addWidget(self.groupBox_3)
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setStyleSheet("border: none;")
        self.widget.setObjectName("widget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_5.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_5.setSpacing(20)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.textEdit = QtWidgets.QTextEdit(self.widget)
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 110))
        self.textEdit.setStyleSheet("border: none;\n"
"background: #eee;\n"
"padding: 15px 15px 15px 85px;\n"
"background-image: url(:/i/i.png);\n"
"background-position:left;\n"
"background-repeat: no-repeat;\n"
"background-size: 50px;\n"
"background-size: cover;")
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_5.addWidget(self.textEdit)
        self.widget_2 = QtWidgets.QWidget(self.widget)
        self.widget_2.setEnabled(False)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_5.addWidget(self.widget_2)
        self.horizontalLayout_2.addWidget(self.widget)
        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p><img src=\":/logo_grey/logo_grey.png\"/></p></body></html>"))
        self.crypto_name.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:9pt; color:#9e9e9e;\">EMT balance</span></p></body></html>"))
        self.crypto_amount.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:9pt; color:#757575;\">49.7289438434637</span></p></body></html>"))
        self.crypto_name_2.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:9pt; color:#9e9e9e;\">MMR balance</span></p></body></html>"))
        self.crypto_amount_2.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:9pt; color:#757575;\">49.7289438434637</span></p></body></html>"))
        self.label_2.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:9pt; color:#797979;\">t23746tdf68c...</span></p></body></html>"))
        self.label_3.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:9pt; color:#9f9f9f;\">Settings</span></p></body></html>"))
        self.upload.setText(_translate("Form", "Upload"))
        self.data_owner_btn.setText(_translate("Form", "Data owner"))
        self.hoster_btn.setText(_translate("Form", "Hoster"))
        self.wallet_btn.setText(_translate("Form", "Wallet"))
        self.miner_btn.setText(_translate("Form", "Miner"))
        self.settings_btn.setText(_translate("Form", "Settings"))
        self.textEdit.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; color:#787878;\">Rudd, gurnad lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim</span></p></body></html>"))

import 1_w_rc
import 2_g_rc
import 3_g_rc
import 4_g_rc
import 5_g_rc
from .resources.angle_rc import *
from .resources.i_rc import *
from .resources.logo_grey_rc import *
from .resources.profile_rc import *
