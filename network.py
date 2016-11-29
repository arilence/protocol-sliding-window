from socket import (
    socket, gethostbyname, gaierror,
    AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_SNDBUF, SHUT_RDWR
)
from threading import Thread
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot, QObject)
from protocol import PWindow, PPacket, PPacketType
from timeit import default_timer
import time, sys, os, collections, ntpath, math
import select as fileSelect
from random import randint

ENCODING_TYPE = "utf-8"

class LogAdapter(QObject):
    logSignal = pyqtSignal(str)
    sentPacketSignal = pyqtSignal(int)
    receivedAckSignal = pyqtSignal(int)

    def __init__(self):
        super(QObject, self).__init__()
        self.logging = True

    def startLogFile(self, fileName):
        fileLoc = os.path.join(".", fileName)
        self.logFile = open(os.path.abspath(fileLoc), 'wb')

    def stopLogFile(self):
        self.logFile.close()

    def logPacket(self, packet):
        packetInfo = "Type: {}, Seq: {}, Ack: {}".format(
            str(packet.packetType), str(packet.seqNum), str(packet.ackNum)
            )
        output = "[{}] {}".format(
            packet.packetType.numToStr(),
            packetInfo
            )
        self.logSignal.emit(output)
        if self.logging:
            self.logFile.write((output + "\n").encode(ENCODING_TYPE))

class NetworkAdapter(LogAdapter):
    def __init__(self):
        super(LogAdapter, self).__init__()
        self.serverHost = ''
        self.controlPort = 7005

    def connect(self, address, port):
        self.sockObj = socket(AF_INET, SOCK_STREAM)      # Create a TCP socket object
        self.sockObj.setsockopt(SOL_SOCKET, SO_SNDBUF, PPacket.PACKET_SIZE)
        self.sockObj.connect((address, port));
        return True

    def disconnect(self):
        packet = PPacket(PPacketType.DCN, 0, 0, 0)
        packet.setData(b'disconnect')
        self.send(packet.toBytes())
        self.sockObj.shutdown(SHUT_RDWR)
        return True

    def send(self, data):
        self.sockObj.sendall(data)

    def receive(self):
        #return self.sockObj.recv(PPacket.PACKET_SIZE)
        n = PPacket.PACKET_SIZE
        data = b''
        while len(data) < n:
            packet = self.sockObj.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

class Transmitter(LogAdapter):
    def __init__(self, network):
        super(LogAdapter, self).__init__()
        self.network = network
        self.sentPackets = 0
        self.receivedAcks = 0
        self.logging = True

    def startSend(self, fileLocation):
        # Check if file really exists
        if not os.path.isfile(fileLocation):
            self.logSignal.emit("[ERROR] File doesn't exist")
            return

        if self.logging:
            self.startLogFile('log-transmitter')

        # Start the send process
        Thread(target=self.send, args=(fileLocation,)).start()
        return True

    def send(self, fileLocation):
        self.windowSize = 10
        self.timeoutTime = 0.5
        self.currentSequenceNumber = 0
        self.generatedSequenceNumber = 0
        self.oldestSequenceNumber = 0
        self.slidingWindow = []
        self.packetTimer = []

        self.sendingFileData = True
        self.doneReadingFile = False
        self.currentState = PPacketType.SYN

        # Get the file ready for reading
        self.theFile = open(fileLocation, 'rb')
        fileSize = os.stat(fileLocation)
        self.tailName = ntpath.basename(fileLocation)

        # Setup Thread for sending packets
        Thread(target=self.sendingFileThread).start()

        # Setup Thread for receiving packets
        Thread(target=self.receivingAckThread).start()

    def sendingFileThread(self):
        while self.sendingFileData:
            # Fill up the sliding window
            while not self.doneReadingFile and len(self.slidingWindow) < self.windowSize:
                if self.currentState == PPacketType.SYN:
                    # Send SYN packet to initiate transfer
                    packet = PPacket(PPacketType.SYN, self.generatedSequenceNumber, self.windowSize, self.generatedSequenceNumber + 1)
                    packet.setData(self.tailName.encode(ENCODING_TYPE))

                    self.slidingWindow.append(packet)
                    self.packetTimer.append([default_timer(), packet])
                    self.logPacket(packet)
                    self.sendThePacket(packet.toBytes())
                    self.currentState = PPacketType.DATA
                    self.generatedSequenceNumber = self.generatedSequenceNumber + 2

                elif self.currentState == PPacketType.DATA:
                    # Read data from file
                    newFileData = self.theFile.read(PPacket.DATA_SIZE)
                    if newFileData:
                        packet = PPacket(PPacketType.DATA, self.generatedSequenceNumber, self.windowSize, self.generatedSequenceNumber + 1)
                        packet.setData(newFileData)

                        self.slidingWindow.append(packet)
                        self.packetTimer.append([default_timer(), packet])
                        self.logPacket(packet)
                        self.sendThePacket(packet.toBytes())
                        self.generatedSequenceNumber = self.generatedSequenceNumber + 2
                    else:
                        self.currentState = PPacketType.EOT

                elif self.currentState == PPacketType.EOT:
                    # Time to finish things up
                    packet = PPacket(PPacketType.EOT, self.generatedSequenceNumber, self.windowSize, self.generatedSequenceNumber + 1)

                    self.slidingWindow.append(packet)
                    self.packetTimer.append([default_timer(), packet])
                    self.logPacket(packet)
                    self.sendThePacket(packet.toBytes())
                    self.doneReadingFile = True
                    self.generatedSequenceNumber = self.generatedSequenceNumber + 2

            # Calculate timed out packets
            for packetTuple in self.packetTimer:
                if default_timer() - packetTuple[0] >= self.timeoutTime:
                    packetTuple[0] = default_timer()
                    self.logPacket(packetTuple[1])
                    self.sendThePacket(packetTuple[1].toBytes())


    def receivingAckThread(self):
        socket = self.network.sockObj

        while self.sendingFileData:
            r, _, _ = fileSelect.select([socket], [], [])
            if r and self.sendingFileData:
                rawData = self.network.receive()
                if rawData:
                    packetResponse = PPacket.parsePacket(rawData)
                    if not packetResponse:
                        return
                    self.logPacket(packetResponse)

                    if packetResponse.packetType == PPacketType.ACK:
                        self.receivedAcks += 1
                        self.receivedAckSignal.emit(self.receivedAcks)

                        # Remove packet with ack number that matches seq number
                        for packetTuple in self.slidingWindow:
                            if packetTuple.ackNum <= packetResponse.seqNum:
                                self.slidingWindow.remove(packetTuple)

                        for packetTuple in self.packetTimer:
                            packet = packetTuple[1]
                            if packet.ackNum <= packetResponse.seqNum:
                                self.packetTimer.remove(packetTuple)

                        # increase sequence number
                        self.currentSequenceNumber = packetResponse.seqNum

                        # if no more packets in sliding window, file finished!
                        if len(self.slidingWindow) <= 0 and self.currentState == PPacketType.EOT:
                            self.logSignal.emit("FILE TRANSFER COMPLETE")
                            self.sendingFileData = False

    def sendThePacket(self, packet):
        self.network.send(packet)
        self.sentPackets += 1
        self.sentPacketSignal.emit(self.sentPackets)

class Receiver(LogAdapter):
    def __init__(self, network):
        super(LogAdapter, self).__init__()
        self.sequenceNumber = 0
        self.keepListening = False
        self.receivingFile = False
        self.logging = True
        self.network = network
        self.directory = 'receiver_files'

    def start(self):
        self.keepListening = True
        Thread(target=self.waitForSocket).start()

    def pause(self):
        self.keepListening = False

    def waitForSocket(self):
        socket = self.network.sockObj

        while self.keepListening:
            r, _, _ = fileSelect.select([socket], [], [])
            if r and self.keepListening:
                # ready to receive
                rawData = self.network.receive()
                if rawData:
                    self.parseData(rawData)
                    #Thread(target=self.parseData, args=(rawData,)).start()

    def parseData(self, data):
        packetInput = PPacket.parsePacket(data)
        if not packetInput:
            return

        self.windowSize = packetInput.windowSize

        # Accept SYN if not currently in the middle of a transfer
        if not self.receivingFile and packetInput.packetType == PPacketType.SYN:
            self.startReceivingFile(packetInput)

        # Accept DATA if in the middle of a transfer
        elif packetInput.packetType == PPacketType.DATA:
            self.receiveData(packetInput)

        # Accept EOT if in the middle of a transfer
        elif packetInput.packetType == PPacketType.EOT:
            self.receiveEOT(packetInput)

        self.logPacket(packetInput)
        self.replyAck(packetInput)

        if not self.receivingFile and packetInput.packetType == PPacketType.EOT:
            if self.logging:
                self.stopLogFile()

    def startReceivingFile(self, packet):
        self.logSignal.emit("START RECEIVING FILE")
        self.sequenceNumber = 0
        self.receivingFile = True
        self.windowSize = packet.windowSize
        self.sequenceNumber = packet.ackNum

        if self.logging:
            self.startLogFile('log-receiver')

        # Make sure the directory exists and file name is correct
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        binaryFileName = packet.data.split(b'\0',1)[0]
        fileName = binaryFileName.decode(ENCODING_TYPE)
        fileLoc = os.path.join(self.directory, str(fileName))
        tailName = ntpath.basename(fileLoc)
        fullPath = os.path.abspath(fileLoc)

        self.theFile = open(fullPath, 'wb')
        if not self.theFile:
            self.theFile = open("temp", 'wb')

    def receiveData(self, packet):
        if self.receivingFile:
            if (self.sequenceNumber + 1) == packet.seqNum:
                self.sequenceNumber = packet.ackNum
                self.theFile.write(packet.data)

    def receiveEOT(self, packet):
        if self.receivingFile:
            if (self.sequenceNumber + 1) == packet.seqNum:
                self.sequenceNumber = packet.ackNum
                self.receivingFile = False
                self.theFile.close()
                self.logSignal.emit("FILE TRANSFER COMPLETE")

    def replyAck(self, packet):
        packetAck = PPacket(PPacketType.ACK, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
        self.logPacket(packetAck)
        self.network.send(packetAck.toBytes())

class Emulator(QObject):
    droppedPacketSignal = pyqtSignal(str)

    def __init__(self):
        super(QObject, self).__init__()
        self.client1 = None
        self.client2 = None
        self.packetCount = 0
        self.bitErrorValue = 0
        self.delayValue = 0
        self.droppedPackets = 0

    def start(self, address, port):
        self.keepListening = True
        Thread(target=self.setupSocket, args=(address, port, self.receive)).start()

    def stop(self):
        self.shutdown()
        self.keepListening = False

    def setBitError(self, newValue):
        self.bitErrorValue = newValue

    def setDelay(self, newValue):
        self.delayValue = newValue

    def setupSocket(self, address, port, clientFunc):
        self.theSocket = socket(AF_INET, SOCK_STREAM)
        self.theSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Bind Socket
        try:
            self.theSocket.bind((address, port))
            self.theSocket.listen(5)
        except:
            print("Socket couldn\'t be binded")
            raise

        # Wait for Connection
        while self.keepListening:
            client, address = self.theSocket.accept()
            if self.client1 is None:
                self.client1 = client
            elif self.client2 is None:
                self.client2 = client
            else:
                self.theSocket.close()
                break

            Thread(target = clientFunc, args = (client, address)).start()

    def receive(self, client, address):
        self.printClients()

        while True:
            n = PPacket.PACKET_SIZE
            theData = b''
            while len(theData) < n:
                packet = client.recv(n - len(theData))
                if not packet:
                    return None
                theData += packet
            rawData = theData

            if not rawData:
                break
            else:
                # packet = PPacket.parsePacket(rawData)
                # if packet.packetType == PPacketType.DCN:
                #     self.removeClient(client)
                #     print("Client Disconnected")
                # else:
                num = randint(0,100)
                if self.bitErrorValue < num:
                    if self.delayValue == 0:
                        self.sendPacket(client, rawData)
                    else:
                        self.delayValue
                else:
                    self.droppedPackets += 1
                    self.droppedPacketSignal.emit(str(self.droppedPackets))

    def sendPacket(self, client, rawData):
        if client is self.client1:
            self.client2.send(rawData)
            print("Client 1 -> Client 2")
        if client is self.client2:
            self.client1.send(rawData)
            print("Client 2 -> Client 1")

    def delayPacket(self, milliseconds, client, rawData):
        waitTime = default_timer()

        while default_timer() - waitTime <= milliseconds:
            self.sendPacket(client, rawData)

    def shutdown(self):
        try:
            self.theSocket.close()
        except Exception as e:
            pass

    def printClients(self):
        client1 = self.client1.getpeername() if self.client1 != None else None
        client2 = self.client2.getpeername() if self.client2 != None else None
        print("Connected Clients: {}, {}".format(client1, client2))

    def removeClient(self, client):
        if client is self.client1:
            self.client1 = None
        elif client is self.client2:
            self.client2 = None
