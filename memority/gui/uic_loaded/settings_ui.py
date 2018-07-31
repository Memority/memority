# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(990, 666)
        Form.setStyleSheet("background: #fff;\n"
"")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setStyleSheet("border: 1px solid #b1b1b1;\n"
"border-radius: 5px;")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setMinimumSize(QtCore.QSize(140, 40))
        self.pushButton.setStyleSheet("font-size: 14px;\n"
"color: #b1b1b1;\n"
"border: 1px solid #b1b1b1;\n"
"border-radius: 5px;")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setMinimumSize(QtCore.QSize(140, 40))
        self.pushButton_2.setStyleSheet("font-size: 14px;\n"
"color: #b1b1b1;\n"
"border: 1px solid #b1b1b1;\n"
"border-radius: 5px;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_5.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setMaximumSize(QtCore.QSize(280, 150))
        self.groupBox_2.setStyleSheet("background-color: #eee;\n"
"background-image: url(:/checked/checked.png);\n"
"background-position: top right;\n"
"background-repeat: no-repeat;\n"
"border-radius: 10px;")
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setStyleSheet("background: none;")
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setStyleSheet("background: none;")
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setStyleSheet("border: none;\n"
"background: #eee;")
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setMaximumSize(QtCore.QSize(280, 150))
        self.groupBox_3.setStyleSheet("background-color: #eee;\n"
"background-image: url(:/checked/checked.png);\n"
"background-position: top right;\n"
"background-repeat: no-repeat;\n"
"border-radius: 10px;")
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setStyleSheet("background: none;")
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setStyleSheet("background: none;")
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.groupBox_3)
        self.textBrowser_2.setStyleSheet("border: none;\n"
"background: #eee;")
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.verticalLayout_2.addWidget(self.textBrowser_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_2.addWidget(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(Form)
        self.groupBox_4.setMaximumSize(QtCore.QSize(280, 150))
        self.groupBox_4.setStyleSheet("background-color: #fff;\n"
"background-image: url(:/not_checked/not_checked.png);\n"
"background-position: top right;\n"
"background-repeat: no-repeat;\n"
"border-radius: 10px;\n"
"border: 1px solid #eee;")
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem5)
        self.label_6 = QtWidgets.QLabel(self.groupBox_4)
        self.label_6.setStyleSheet("background: none;\n"
"border: none;")
        self.label_6.setObjectName("label_6")
        self.verticalLayout_3.addWidget(self.label_6)
        self.label_7 = QtWidgets.QLabel(self.groupBox_4)
        self.label_7.setStyleSheet("background: none;\n"
"border: none;")
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.textBrowser_3 = QtWidgets.QTextBrowser(self.groupBox_4)
        self.textBrowser_3.setStyleSheet("border: none;\n"
"background: #fff;")
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.verticalLayout_3.addWidget(self.textBrowser_3)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem6)
        self.horizontalLayout_2.addWidget(self.groupBox_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_5.addWidget(self.label_8)
        self.groupBox_5 = QtWidgets.QGroupBox(Form)
        self.groupBox_5.setMinimumSize(QtCore.QSize(0, 169))
        self.groupBox_5.setStyleSheet("border: 1px solid #b1b1b1;\n"
"border-radius: 5px;")
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox_5)
        self.groupBox_7.setMinimumSize(QtCore.QSize(0, 70))
        self.groupBox_7.setStyleSheet("border: none;")
        self.groupBox_7.setTitle("")
        self.groupBox_7.setObjectName("groupBox_7")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_7)
        self.groupBox_6.setMinimumSize(QtCore.QSize(170, 0))
        self.groupBox_6.setStyleSheet("border: none;")
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.label_9 = QtWidgets.QLabel(self.groupBox_6)
        self.label_9.setGeometry(QtCore.QRect(0, 10, 141, 21))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.groupBox_6)
        self.label_10.setGeometry(QtCore.QRect(0, 30, 131, 21))
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_5.addWidget(self.groupBox_6)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_7)
        self.spinBox.setMaximumSize(QtCore.QSize(40, 16777215))
        self.spinBox.setStyleSheet("border-radius: 0;")
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_3.addWidget(self.spinBox)
        self.label_11 = QtWidgets.QLabel(self.groupBox_7)
        self.label_11.setStyleSheet("border-radius: 0;")
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_3.addWidget(self.label_11)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem7)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)
        self.verticalLayout_4.addWidget(self.groupBox_7)
        self.groupBox_8 = QtWidgets.QGroupBox(self.groupBox_5)
        self.groupBox_8.setMinimumSize(QtCore.QSize(170, 0))
        self.groupBox_8.setStyleSheet("border: none;")
        self.groupBox_8.setTitle("")
        self.groupBox_8.setObjectName("groupBox_8")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBox_8)
        self.horizontalLayout_7.setSpacing(10)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_12 = QtWidgets.QLabel(self.groupBox_8)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_7.addWidget(self.label_12)
        self.label_13 = QtWidgets.QLabel(self.groupBox_8)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_7.addWidget(self.label_13)
        self.label_14 = QtWidgets.QLabel(self.groupBox_8)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_7.addWidget(self.label_14)
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_8)
        self.pushButton_5.setMinimumSize(QtCore.QSize(160, 40))
        self.pushButton_5.setStyleSheet("font-size: 16px;\n"
"color: #757575;\n"
"border: 1px solid #757575;\n"
"border-radius: 7px;")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_7.addWidget(self.pushButton_5)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem8)
        self.verticalLayout_4.addWidget(self.groupBox_8)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_3.setMinimumSize(QtCore.QSize(100, 40))
        self.pushButton_3.setStyleSheet("font-size: 14px;\n"
"color: #b1b1b1;\n"
"border: 1px solid #b1b1b1;\n"
"border-radius: 5px;")
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_4.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_4.setMinimumSize(QtCore.QSize(100, 40))
        self.pushButton_4.setStyleSheet("font-size: 14px;\n"
"color: #b1b1b1;\n"
"border: 1px solid #b1b1b1;\n"
"border-radius: 5px;")
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_4.addWidget(self.pushButton_4)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem9)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.verticalLayout_5.addWidget(self.groupBox_5)
        spacerItem10 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem10)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">Account settings</span></p></body></html>"))
        self.pushButton.setText(_translate("Form", "Import account"))
        self.pushButton_2.setText(_translate("Form", "Export account"))
        self.label_2.setText(_translate("Form", "<html><head/><body><p align=\"center\"><img src=\":/owner_set/owner_set.png\"/></p></body></html>"))
        self.label_3.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600; color:#757575;\">Data owner</span></p></body></html>"))
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#a9a9a9;\">Aermekf sjeflfb feklf of fjsf Hkfs. Ghjd jkld dkk nkfndjskf</span></p></body></html>"))
        self.label_4.setText(_translate("Form", "<html><head/><body><p align=\"center\"><img src=\":/hoster/hoster.png\"/></p></body></html>"))
        self.label_5.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600; color:#757575;\">Hosted</span></p></body></html>"))
        self.textBrowser_2.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#a9a9a9;\">Aermekf sjeflfb feklf of fjsf Hkfs. Ghjd jkld dkk nkfndjskf</span></p></body></html>"))
        self.label_6.setText(_translate("Form", "<html><head/><body><p align=\"center\"><img src=\":/miner_set/miner_set.png\"/></p></body></html>"))
        self.label_7.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600; color:#757575;\">Miner</span></p></body></html>"))
        self.textBrowser_3.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#a9a9a9;\">Earned tokens:<br />0,89898 MMR</span></p></body></html>"))
        self.label_8.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:16pt;\">Hosting settings</span></p></body></html>"))
        self.label_9.setText(_translate("Form", "Disk space for hosting"))
        self.label_10.setText(_translate("Form", "<html><head/><body><p><span style=\" color:#bebebe;\">Total available 500 GB</span></p></body></html>"))
        self.label_11.setText(_translate("Form", " GB"))
        self.label_12.setText(_translate("Form", "Directory to store files"))
        self.label_13.setText(_translate("Form", "<html><head/><body><p><span style=\" color:#757575;\">../fdgmd/fdgmkl/fsdsf/sdfmdsfsfdm</span></p></body></html>"))
        self.label_14.setText(_translate("Form", "<html><head/><body><p><img src=\":/ch_dir/change_directory.png\"/></p></body></html>"))
        self.pushButton_5.setText(_translate("Form", "Change directory"))
        self.pushButton_3.setText(_translate("Form", "Apply"))
        self.pushButton_4.setText(_translate("Form", "Reset"))

from .resources.ch_dir_rc import *
from .resources.change_directory_rc import *
from .resources.checked_rc import *
from .resources.hoster_rc import *
from .resources.miner_set_rc import *
from .resources.not_checked_rc import *
from .resources.owner_set_rc import *
