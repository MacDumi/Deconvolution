# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'crop_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(284, 145)
        Dialog.setMaximumSize(QtCore.QSize(284, 145))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../graphics/icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.lineEdit_min = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit_min.setFont(font)
        self.lineEdit_min.setObjectName("lineEdit_min")
        self.gridLayout.addWidget(self.lineEdit_min, 2, 0, 1, 1)
        self.lineEdit_max = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit_max.setFont(font)
        self.lineEdit_max.setObjectName("lineEdit_max")
        self.gridLayout.addWidget(self.lineEdit_max, 2, 2, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.lbl_max = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_max.setFont(font)
        self.lbl_max.setText("")
        self.lbl_max.setObjectName("lbl_max")
        self.gridLayout.addWidget(self.lbl_max, 1, 2, 1, 1)
        self.lbl_min = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_min.setFont(font)
        self.lbl_min.setText("")
        self.lbl_min.setObjectName("lbl_min")
        self.gridLayout.addWidget(self.lbl_min, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEdit_min, self.lineEdit_max)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Crop to"))
