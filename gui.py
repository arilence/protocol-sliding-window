"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        gui.py - file that holds the gui initialization
--
--      PROGRAM:            file_transport
--
--      FUNCTIONS:          __init__(self)
--                          toggleServer(self)
--                          startServer(self)
--                          stopServer(self)
--                          bitErrorChanged(self, newValue)
--                          bitTextChanged(self, newValue)
--                          delayChanged(self, newValue)
--                          delayTextChanged(self, newValue)
--                          dropPacket(self, value)
--                          setConnected(self, connected)
--                          connectPressed(self)
--                          setMode(self, index)
--                          changeTab(self, checked)
--                          updateLogging(self,checked)
--                          sendFile(self)
--                          browseFiles(self)
--                          logMessage(self)
--                          clearLogMessages(self)
--                          updateSentPackets(self, num)
--                          updateRecvAcks(self, value)
--
--      DATE:               November 29, 2016
--
--      REVISION:           (Date and Description)
--
--      DESIGNERS:          Anthony Smith and Spenser Lee
--
--      PROGRAMMERS:        Anthony Smith and Spenser Lee
--
--      NOTES:
--      This file contains the gui initialization to show an interface to the user.
--      The Transmitter and Receiver network classes use the same GUI to ease of access.
--      Where the network emulator has a seperate interface to display dropped packets,
--      bit error rate, and delay per packet.
---------------------------------------------------------------------------------------"""
import sys, ntpath, os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from ui.ui_client import Ui_Client
from ui.ui_emulator import Ui_Emulator
from network import *

"""---------------------------------------------------------------------------------------
-- CLASS:      Application
-- DATE:       29/11/2016
-- REVISIONS:  (V1.0)
-- DESIGNER:   Anthony Smith
-- PROGRAMMER: Anthony Smith
--
-- NOTES:
-- PyQt5's main wrapper for holding QWindows inside. Provides a GUI frame that can be filled
--------------------------------------------------------------------------------------"""
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

"""---------------------------------------------------------------------------------------
-- CLASS:      EmulatorWindow
-- DATE:       29/11/2016
-- REVISIONS:  (V1.0)
-- DESIGNER:   Anthony Smith
-- PROGRAMMER: Anthony Smith
--
-- NOTES:
-- Renders the user interface for the emulator window
--------------------------------------------------------------------------------------"""
class EmulatorWindow(QMainWindow, Ui_Emulator):
    def __init__(self, Ui_Client, client, parent=None):
        super(EmulatorWindow, self).__init__(parent)
        self.serverRunning = False
        self.setupUi(self)
        self.startServerBtn.clicked.connect(self.toggleServer)
        self.bitErrorSlider.valueChanged.connect(self.bitErrorChanged)
        self.bitErrorText.textChanged.connect(self.bitTextChanged)
        self.delaySlider.valueChanged.connect(self.delayChanged)
        self.delayText.textChanged.connect(self.delayTextChanged)

        self.emulator = Emulator()
        self.emulator.droppedPacketSignal.connect(self.dropPacket)

    def toggleServer(self):
        if self.serverRunning:
            self.serverRunning = False
            self.stopServer()
        else:
            self.serverRunning = True
            self.startServer()

    def startServer(self):
        self.startServerBtn.setText("Stop Server")
        self.addressInput.setDisabled(True)
        self.portInput.setDisabled(True)
        self.emulator.start(self.addressInput.text(), int(self.portInput.text()))

    def stopServer(self):
        self.startServerBtn.setText("Start Server")
        self.addressInput.setDisabled(False)
        self.portInput.setDisabled(False)
        self.emulator.stop()

    def bitErrorChanged(self, newValue):
        try:
            self.bitErrorText.setText(str(newValue))
            self.emulator.setBitError(int(newValue))
        except ValueError as e:
            pass

    def bitTextChanged(self, newValue):
        try:
            self.bitErrorSlider.setValue(int(newValue))
            self.emulator.setBitError(int(newValue))
        except ValueError as e:
            pass

    def delayChanged(self, newValue):
        try:
            self.delayText.setText(str(newValue))
            self.emulator.setDelay(int(newValue))
        except ValueError as e:
            pass

    def delayTextChanged(self, newValue):
        try:
            self.delaySlider.setValue(int(newValue))
            self.emulator.setDelay(int(newValue))
        except ValueError as e:
            pass

    def dropPacket(self, value):
        self.droppedPackets.setText("Dropped Packets: " + value)


"""---------------------------------------------------------------------------------------
-- CLASS:      ClassWindow
-- DATE:       29/11/2016
-- REVISIONS:  (V1.0)
-- DESIGNER:   Anthony Smith
-- PROGRAMMER: Anthony Smith
--
-- NOTES:
-- Renders the user interface for the client window (transmitter and receiver)
--------------------------------------------------------------------------------------"""
class ClientWindow(QMainWindow, Ui_Client):
    def __init__(self, Ui_Client, transmitter, parent=None):
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
        self.transmitter.sentPacketSignal.connect(self.updateSentPackets)
        self.transmitter.receivedAckSignal.connect(self.updateRecvAcks)

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

    def updateSentPackets(self, num):
        self.sentPackets.setText("Sent Packets: " + str(num))

    def updateRecvAcks(self, value):
        self.receivedAcks2.setText("Recv Acks: " + str(value))
