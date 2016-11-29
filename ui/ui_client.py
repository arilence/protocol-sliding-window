# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/ui_client.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Client(object):
    def setupUi(self, Client):
        Client.setObjectName("Client")
        Client.setEnabled(True)
        Client.resize(711, 538)
        Client.setWindowTitle("")
        Client.setAnimated(True)
        Client.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(Client)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.connectionBox = QtWidgets.QHBoxLayout()
        self.connectionBox.setObjectName("connectionBox")
        self.addressInput = QtWidgets.QLineEdit(self.centralwidget)
        self.addressInput.setMinimumSize(QtCore.QSize(100, 0))
        self.addressInput.setMaximumSize(QtCore.QSize(220, 16777215))
        self.addressInput.setMaxLength(45)
        self.addressInput.setObjectName("addressInput")
        self.connectionBox.addWidget(self.addressInput)
        self.portInput = QtWidgets.QLineEdit(self.centralwidget)
        self.portInput.setMinimumSize(QtCore.QSize(50, 0))
        self.portInput.setMaximumSize(QtCore.QSize(100, 16777215))
        self.portInput.setMaxLength(10)
        self.portInput.setObjectName("portInput")
        self.connectionBox.addWidget(self.portInput)
        self.connectBtn = QtWidgets.QPushButton(self.centralwidget)
        self.connectBtn.setEnabled(True)
        self.connectBtn.setMaximumSize(QtCore.QSize(100, 16777215))
        self.connectBtn.setObjectName("connectBtn")
        self.connectionBox.addWidget(self.connectBtn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.connectionBox.addItem(spacerItem)
        self.verticalLayout.addLayout(self.connectionBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.modeTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.modeTabWidget.setMinimumSize(QtCore.QSize(0, 130))
        self.modeTabWidget.setBaseSize(QtCore.QSize(0, 100))
        self.modeTabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.modeTabWidget.setTabsClosable(False)
        self.modeTabWidget.setTabBarAutoHide(False)
        self.modeTabWidget.setObjectName("modeTabWidget")
        self.transmitTab = QtWidgets.QWidget()
        self.transmitTab.setMinimumSize(QtCore.QSize(0, 0))
        self.transmitTab.setObjectName("transmitTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.transmitTab)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horiWidget = QtWidgets.QWidget(self.transmitTab)
        self.horiWidget.setMinimumSize(QtCore.QSize(0, 100))
        self.horiWidget.setObjectName("horiWidget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.horiWidget)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.fileLocationInput = QtWidgets.QLineEdit(self.horiWidget)
        self.fileLocationInput.setMinimumSize(QtCore.QSize(0, 20))
        self.fileLocationInput.setObjectName("fileLocationInput")
        self.horizontalLayout.addWidget(self.fileLocationInput)
        self.fileLocationBtn = QtWidgets.QPushButton(self.horiWidget)
        self.fileLocationBtn.setObjectName("fileLocationBtn")
        self.horizontalLayout.addWidget(self.fileLocationBtn)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.sendBtn = QtWidgets.QPushButton(self.horiWidget)
        self.sendBtn.setObjectName("sendBtn")
        self.verticalLayout_3.addWidget(self.sendBtn)
        self.horizontalLayout_6.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.sentPackets = QtWidgets.QLabel(self.horiWidget)
        self.sentPackets.setObjectName("sentPackets")
        self.verticalLayout_4.addWidget(self.sentPackets)
        self.receivedAcks2 = QtWidgets.QLabel(self.horiWidget)
        self.receivedAcks2.setObjectName("receivedAcks2")
        self.verticalLayout_4.addWidget(self.receivedAcks2)
        self.horizontalLayout_6.addLayout(self.verticalLayout_4)
        self.verticalLayout_2.addWidget(self.horiWidget)
        self.modeTabWidget.addTab(self.transmitTab, "")
        self.receiveTab = QtWidgets.QWidget()
        self.receiveTab.setObjectName("receiveTab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.receiveTab)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridWidget = QtWidgets.QWidget(self.receiveTab)
        self.gridWidget.setObjectName("gridWidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.gridWidget)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_3 = QtWidgets.QLabel(self.gridWidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.horizontalLayout_4.addWidget(self.gridWidget)
        self.modeTabWidget.addTab(self.receiveTab, "")
        self.verticalLayout.addWidget(self.modeTabWidget)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.logOutputLabel = QtWidgets.QLabel(self.centralwidget)
        self.logOutputLabel.setObjectName("logOutputLabel")
        self.verticalLayout.addWidget(self.logOutputLabel)
        self.logOutput = QtWidgets.QListWidget(self.centralwidget)
        self.logOutput.setObjectName("logOutput")
        self.verticalLayout.addWidget(self.logOutput)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.clearLogBtn = QtWidgets.QPushButton(self.centralwidget)
        self.clearLogBtn.setObjectName("clearLogBtn")
        self.horizontalLayout_2.addWidget(self.clearLogBtn)
        self.logCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.logCheckBox.setMaximumSize(QtCore.QSize(150, 16777215))
        self.logCheckBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.logCheckBox.setChecked(True)
        self.logCheckBox.setObjectName("logCheckBox")
        self.horizontalLayout_2.addWidget(self.logCheckBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        Client.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Client)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 711, 22))
        self.menubar.setObjectName("menubar")
        Client.setMenuBar(self.menubar)

        self.retranslateUi(Client)
        self.modeTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Client)

    def retranslateUi(self, Client):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Client", "Connection Details"))
        self.addressInput.setText(_translate("Client", "localhost"))
        self.addressInput.setPlaceholderText(_translate("Client", "Address"))
        self.portInput.setText(_translate("Client", "7005"))
        self.portInput.setPlaceholderText(_translate("Client", "Port"))
        self.connectBtn.setText(_translate("Client", "Connect"))
        self.label_2.setText(_translate("Client", "Data Configuration"))
        self.fileLocationBtn.setText(_translate("Client", "Browse"))
        self.sendBtn.setText(_translate("Client", "Send File"))
        self.sentPackets.setText(_translate("Client", "Sent Packets: 0"))
        self.receivedAcks2.setText(_translate("Client", "Recv Acks: 0"))
        self.modeTabWidget.setTabText(self.modeTabWidget.indexOf(self.transmitTab), _translate("Client", "Transmitter"))
        self.label_3.setText(_translate("Client", "File will be saved in the folder receiver_files/"))
        self.modeTabWidget.setTabText(self.modeTabWidget.indexOf(self.receiveTab), _translate("Client", "Receiver"))
        self.logOutputLabel.setText(_translate("Client", "Log Output"))
        self.clearLogBtn.setText(_translate("Client", "Clear Log"))
        self.logCheckBox.setText(_translate("Client", "Save Log"))

