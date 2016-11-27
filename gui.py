import sys, ntpath, os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from ui.ui_transmitter import Ui_Transmitter
from network import *

class Application():
    def __init__(self, sysArgv, title):
        app = QApplication(sysArgv)

        window = TransmitterWindow(Ui_Transmitter(), title)
        window.show()
        sys.exit(app.exec_())

class TransmitterWindow(QMainWindow, Ui_Transmitter):
    APP_NAME = "Transfer App"
    WINDOW_HEIGHT = 250
    WINDOW_WIDTH = 500

    def __init__(self, Ui_Transmitter, transmitter, parent=None):
        super(TransmitterWindow, self).__init__(parent)

        # Connect UI Elements
        self.setupUi(self)
        self.connectBtn.clicked.connect(self.connectPressed)
        self.sendBtn.clicked.connect(self.sendFile)
        self.clearLogBtn.clicked.connect(self.clearLogMessages)
        self.modeTabWidget.currentChanged.connect(self.changeTab)
        self.modeTabWidget.setCurrentIndex(0)
        self.fileLocationBtn.clicked.connect(self.browseFiles)

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
                result = self.network.connect("", 7005)
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

    def sendFile(self):
        fileLocation = self.fileLocationInput.text()
        self.transmitter.startSend(fileLocation)

    def browseFiles(self):
        filename = QFileDialog.getOpenFileName(self, "Open File")
        if not filename[0]:
            self.logMessage("[FILE] No file selected")
            return False
        else:
            self.logMessage("[FILE] " + filename[0])
            return filename

    def logMessage(self, log):
        self.logOutput.addItem(log)

    def clearLogMessages(self):
        self.logOutput.clear()
