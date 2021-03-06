# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1121, 740)
        MainWindow.setMinimumSize(QtCore.QSize(888, 607))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("graphics/icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Triangular)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.ForceTabbedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1121, 34))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuDeconvolution = QtWidgets.QMenu(self.menubar)
        self.menuDeconvolution.setObjectName("menuDeconvolution")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuDeconvolution_2 = QtWidgets.QMenu(self.menubar)
        self.menuDeconvolution_2.setObjectName("menuDeconvolution_2")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
        self.dockGuess = QtWidgets.QDockWidget(MainWindow)
        self.dockGuess.setWindowIcon(icon)
        self.dockGuess.setToolTip("")
        self.dockGuess.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.dockGuess.setObjectName("dockGuess")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.dockWidgetContents_2)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(12)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(11, item)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(20)
        self.tableWidget.verticalHeader().setDefaultSectionSize(30)
        self.tableWidget.verticalHeader().setMinimumSectionSize(20)
        self.tableWidget.verticalHeader().setSortIndicatorShown(True)
        self.horizontalLayout.addWidget(self.tableWidget)
        self.dockGuess.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockGuess)
        self.dockOut = QtWidgets.QDockWidget(MainWindow)
        self.dockOut.setObjectName("dockOut")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.textOut = QtWidgets.QTextEdit(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.textOut.setFont(font)
        self.textOut.setAcceptRichText(True)
        self.textOut.setObjectName("textOut")
        self.gridLayout_3.addWidget(self.textOut, 0, 0, 1, 1)
        self.dockOut.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockOut)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionToolbar = QtWidgets.QAction(MainWindow)
        self.actionToolbar.setCheckable(True)
        self.actionToolbar.setChecked(True)
        self.actionToolbar.setObjectName("actionToolbar")
        self.actionGuess = QtWidgets.QAction(MainWindow)
        self.actionGuess.setCheckable(True)
        self.actionGuess.setChecked(True)
        self.actionGuess.setObjectName("actionGuess")
        self.actionCrop = QtWidgets.QAction(MainWindow)
        self.actionCrop.setObjectName("actionCrop")
        self.actionRemove_Baseline = QtWidgets.QAction(MainWindow)
        self.actionRemove_Baseline.setObjectName("actionRemove_Baseline")
        self.actionOutput = QtWidgets.QAction(MainWindow)
        self.actionOutput.setCheckable(True)
        self.actionOutput.setChecked(True)
        self.actionOutput.setObjectName("actionOutput")
        self.actionSpike_Removal = QtWidgets.QAction(MainWindow)
        self.actionSpike_Removal.setObjectName("actionSpike_Removal")
        self.actionSmoothing = QtWidgets.QAction(MainWindow)
        self.actionSmoothing.setObjectName("actionSmoothing")
        self.actionDeconvolute = QtWidgets.QAction(MainWindow)
        self.actionDeconvolute.setObjectName("actionDeconvolute")
        self.actionLoadGuess = QtWidgets.QAction(MainWindow)
        self.actionLoadGuess.setObjectName("actionLoadGuess")
        self.actionExportGuess = QtWidgets.QAction(MainWindow)
        self.actionExportGuess.setObjectName("actionExportGuess")
        self.actionLoad_defaults = QtWidgets.QAction(MainWindow)
        self.actionLoad_defaults.setObjectName("actionLoad_defaults")
        self.actionDeconvolute_MCMC = QtWidgets.QAction(MainWindow)
        self.actionDeconvolute_MCMC.setObjectName("actionDeconvolute_MCMC")
        self.actionBatch_deconvolution = QtWidgets.QAction(MainWindow)
        self.actionBatch_deconvolution.setObjectName("actionBatch_deconvolution")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuDeconvolution.addAction(self.actionCrop)
        self.menuDeconvolution.addAction(self.actionRemove_Baseline)
        self.menuDeconvolution.addAction(self.actionSpike_Removal)
        self.menuDeconvolution.addAction(self.actionSmoothing)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionToolbar)
        self.menuView.addAction(self.actionGuess)
        self.menuView.addAction(self.actionOutput)
        self.menuDeconvolution_2.addSeparator()
        self.menuDeconvolution_2.addAction(self.actionDeconvolute)
        self.menuDeconvolution_2.addAction(self.actionDeconvolute_MCMC)
        self.menuDeconvolution_2.addAction(self.actionBatch_deconvolution)
        self.menuDeconvolution_2.addSeparator()
        self.menuDeconvolution_2.addAction(self.actionLoadGuess)
        self.menuDeconvolution_2.addAction(self.actionLoad_defaults)
        self.menuDeconvolution_2.addAction(self.actionExportGuess)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuDeconvolution.menuAction())
        self.menubar.addAction(self.menuDeconvolution_2.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Raman Deconvolution"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuDeconvolution.setTitle(_translate("MainWindow", "Processing"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuDeconvolution_2.setTitle(_translate("MainWindow", "Deconvolution"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.dockGuess.setWindowTitle(_translate("MainWindow", "Initial Guess"))
        self.tableWidget.setSortingEnabled(True)
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Use"))
        item.setToolTip(_translate("MainWindow", "Used for deconvolution"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Band"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Position, cm-1"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Position low, cm-1"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Positon high, cm-1"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Intensity"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Intensity low"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Intensity high"))
        item = self.tableWidget.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Width"))
        item = self.tableWidget.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "Width low"))
        item = self.tableWidget.horizontalHeaderItem(10)
        item.setText(_translate("MainWindow", "Width high"))
        item = self.tableWidget.horizontalHeaderItem(11)
        item.setText(_translate("MainWindow", "Shape"))
        self.dockOut.setWindowTitle(_translate("MainWindow", "Output"))
        self.actionNew.setText(_translate("MainWindow", "Open"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionToolbar.setText(_translate("MainWindow", "Toolbar"))
        self.actionGuess.setText(_translate("MainWindow", "Initial Guess"))
        self.actionCrop.setText(_translate("MainWindow", "Crop"))
        self.actionCrop.setShortcut(_translate("MainWindow", "Ctrl+Shift+C"))
        self.actionRemove_Baseline.setText(_translate("MainWindow", "Remove Baseline"))
        self.actionRemove_Baseline.setShortcut(_translate("MainWindow", "Ctrl+Shift+B"))
        self.actionOutput.setText(_translate("MainWindow", "Output"))
        self.actionSpike_Removal.setText(_translate("MainWindow", "Spike Removal"))
        self.actionSmoothing.setText(_translate("MainWindow", "Smoothing"))
        self.actionSmoothing.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionDeconvolute.setText(_translate("MainWindow", "Deconvolute"))
        self.actionDeconvolute.setShortcut(_translate("MainWindow", "Ctrl+Shift+D"))
        self.actionLoadGuess.setText(_translate("MainWindow", "Load guess parameters"))
        self.actionExportGuess.setText(_translate("MainWindow", "Export guess parameters"))
        self.actionLoad_defaults.setText(_translate("MainWindow", "Load default guess parameters"))
        self.actionDeconvolute_MCMC.setText(_translate("MainWindow", "Deconvolute (MCMC)"))
        self.actionDeconvolute_MCMC.setShortcut(_translate("MainWindow", "Ctrl+Shift+M"))
        self.actionBatch_deconvolution.setText(_translate("MainWindow", "Batch deconvolution"))
