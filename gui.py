import sys, ntpath, os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from ui.ui_client import Ui_Client
from ui.ui_emulator import Ui_Emulator
from network import *

class Application():
    def __init__(self, sysArgv, title, emulator):
        app = QApplication(sysArgv)

        if emulator:
            window = EmulatorWindow(Ui_Emulator(), title)
            window.show()
        else:
            window = ClientWindow(Ui_Client(), title)
            window.show()
        sys.exit(app.exec_())

class EmulatorWindow(QMainWindow, Ui_Emulator):
    def __init__(self, Ui_Client, client, parent=None):
        super(EmulatorWindow, self).__init__(parent)
        self.setupUi(self)

class ClientWindow(QMainWindow, Ui_Client):
    APP_NAME = "Transfer App"
    WINDOW_HEIGHT = 250
    WINDOW_WIDTH = 500

    def __init__(self, Ui_Client, client, parent=None):
        super(ClientWindow, self).__init__(parent)

        # Connect UI Elements
        self.setupUi(self)
        self.connectBtn.clicked.connect(self.connectPressed)
        self.sendBtn.clicked.connect(self.sendFile)
        self.clearLogBtn.clicked.connect(self.clearLogMessages)
        self.modeTabWidget.currentChanged.connect(self.changeTab)
        self.modeTabWidget.setCurrentIndex(0)
        self.fileLocationBtn.clicked.connect(self.browseFiles)
        self.logCheckBox.clicked.connect(self.updateLogging)

        # Setup Network
        self.setConnected(False)
        self.network = NetworkAdapter()
        self.transmitter = Transmitter(self.network)
        self.receiver = Receiver(self.network)
        self.setMode(0)

        # Connect Network to Logging System
        self.network.logSignal.connect(self.logMessage)
        self.transmitter.logSignal.connect(self.logMessage)
        self.receiver.logSignal.connect(self.logMessage)

    def setConnected(self, connected):
        self.isConnected = connected
        if self.isConnected:
            self.addressInput.setDisabled(True)
            self.portInput.setDisabled(True)
            self.connectBtn.setText("Disconnect")
            self.sendBtn.setDisabled(False)
            self.modeTabWidget.setDisabled(False)
            self.fileLocationBtn.setDisabled(False)
        else:
            self.addressInput.setDisabled(False)
            self.portInput.setDisabled(False)
            self.connectBtn.setText("Connect")
            self.sendBtn.setDisabled(True)
            self.modeTabWidget.setDisabled(True)
            self.fileLocationBtn.setDisabled(True)

    def connectPressed(self):
        if self.isConnected:
            result = self.network.disconnect()
            if result:
                self.setConnected(False)
                self.modeTabWidget.setCurrentIndex(0)   # set tab back to transmit
        else:
            try:
                result = self.network.connect(self.addressInput.text(), int(self.portInput.text()))
                if result == True:
                    self.setConnected(True)
                else:
                    self.logMessage("[ERROR] Cannot connect to remote")
            except Exception as exc:
                self.logMessage("[ERROR] Cannot connect to remote")

    def setMode(self, index):
        if (index == 0):
            self.receiver.pause()
            if self.isConnected:
                self.logMessage("[INFO] Changed to Transmitter mode")
        elif (index == 1):
            self.receiver.start()
            if self.isConnected:
                self.logMessage("[INFO] Changed to Receiver mode")

    def changeTab(self, index):
        self.setMode(index)

    def updateLogging(self, checked):
        self.transmitter.logging = checked
        self.receiver.logging = checked

    def sendFile(self):
        fileLocation = self.fileLocationInput.text()
        self.transmitter.startSend(fileLocation)

    def browseFiles(self):
        fileName = QFileDialog.getOpenFileName(self, "Open File")
        if not fileName[0]:
            self.logMessage("[FILE] No file selected")
            return False
        else:
            self.logMessage("[FILE] " + fileName[0])
            self.fileLocationInput.setText(fileName[0])
            return fileName

    def logMessage(self, log):
        self.logOutput.addItem(log)

    def clearLogMessages(self):
        self.logOutput.clear()
