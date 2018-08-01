# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Memority(object):
    def setupUi(self, Memority):
        Memority.setObjectName("Memority")
        Memority.resize(972, 667)
        Memority.setStyleSheet("background: #fff;")
        self.centralwidget = QtWidgets.QWidget(Memority)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        Memority.setCentralWidget(self.centralwidget)

        self.retranslateUi(Memority)
        QtCore.QMetaObject.connectSlotsByName(Memority)

    def retranslateUi(self, Memority):
        _translate = QtCore.QCoreApplication.translate
        Memority.setWindowTitle(_translate("Memority", "Memority"))

