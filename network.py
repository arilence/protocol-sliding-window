from socket import (
    socket, gethostbyname, gaierror,
    AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_SNDBUF, SHUT_RDWR
)
from threading import Thread
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot, QObject)
from protocol import PWindow, PPacket, PPacketType
from timeit import default_timer
import time, sys, os, collections, ntpath
import select as fileSelect
from random import randint

ENCODING_TYPE = "utf-8"

class LogAdapter(QObject):
    logSignal = pyqtSignal(str)

    def __init__(self):
        super(QObject, self).__init__()

    def logPacket(self, packet):
        packetInfo = "Type: {}, Seq: {}, Ack: {}".format(
            str(packet.packetType), str(packet.seqNum), str(packet.ackNum)
            )
        self.logSignal.emit("[{}] {}".format(
            packet.packetType.numToStr(),
            packetInfo
            ))

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
        #self.sockObj.send(str(data).encode(ENCODING_TYPE))
        self.sockObj.send(data)

    def receive(self):
        return self.sockObj.recv(PPacket.PACKET_SIZE)

class Transmitter(LogAdapter):
    def __init__(self, network):
        super(LogAdapter, self).__init__()
        self.network = network

    def startSend(self, fileLocation):
        # Check if file really exists
        if not os.path.isfile(fileLocation):
            self.logSignal.emit("[ERROR] File doesn't exist")
            return

        # Start the send process
        Thread(target=self.send, args=(fileLocation,)).start()
        return True

    def send(self, fileLocation):
        self.sequenceNumber = 0
        self.windowSize = 1
        self.sendingFileData = True
        self.shouldSend = True
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
        # Send all of the file data
        self.slidingWindow = collections.deque()
        sendTime = default_timer()

        while self.sendingFileData:
            if self.currentState == PPacketType.SYN:
                if self.shouldSend:
                    packetInitial = PPacket(PPacketType.SYN, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
                    packetInitial.setData(self.tailName.encode(ENCODING_TYPE))
                    self.logPacket(packetInitial)
                    self.network.send(packetInitial.toBytes())
                    sendTime = default_timer()
                    self.shouldSend = False

            elif self.currentState == PPacketType.DATA:
                if len(self.slidingWindow) < self.windowSize and not self.doneReadingFile:
                    newFileData = self.theFile.read(PPacket.DATA_SIZE)
                    if newFileData:
                        packet = PPacket(PPacketType.DATA, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
                        packet.setData(newFileData)
                        self.slidingWindow.append(packet)
                    else:
                        self.doneReadingFile = True

                if self.shouldSend:
                    tempSlidingWindow = self.slidingWindow.copy()
                    for index in range(len(tempSlidingWindow)):
                        transferPacket = tempSlidingWindow.popleft()
                        self.logPacket(transferPacket)
                        self.network.send(transferPacket.toBytes())
                    sendTime = default_timer()
                    self.shouldSend = False

            elif self.currentState == PPacketType.EOT:
                if self.shouldSend:
                    packetEot = PPacket(PPacketType.EOT, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
                    self.logPacket(packetEot)
                    self.network.send(packetEot.toBytes())
                    sendTime = default_timer()
                    self.shouldSend = False

            if default_timer() - sendTime >= 0.1:
                if self.doneReadingFile:
                    self.currentState =PPacketType.EOT
                self.shouldSend = True

    def receivingAckThread(self):
        socket = self.network.sockObj

        while self.sendingFileData:
            r, _, _ = fileSelect.select([socket], [], [])
            if r and self.sendingFileData:
                rawData = self.network.receive()
                #data = rawData.decode(ENCODING_TYPE)
                if rawData:
                    packetResponse = PPacket.parsePacket(rawData)
                    if not packetResponse:
                        return
                    self.logPacket(packetResponse)

                    if packetResponse.seqNum == self.sequenceNumber + 1 and packetResponse.packetType == PPacketType.ACK:
                        if self.currentState == PPacketType.SYN:
                            self.currentState = PPacketType.DATA
                            self.shouldSend = True
                            self.sequenceNumber = packetResponse.ackNum
                        elif self.currentState == PPacketType.DATA:
                            if self.doneReadingFile:
                                self.currentState = PPacketType.EOT

                            diff = packetResponse.seqNum - self.sequenceNumber
                            for num in range(0, diff):
                                self.slidingWindow.popleft()
                            self.sequenceNumber = packetResponse.ackNum
                            self.shouldSend = True

                        elif self.currentState == PPacketType.EOT:
                            self.logSignal.emit("FILE TRANSFER COMPLETE")
                            self.sendingFileData = False

class Receiver(LogAdapter):
    def __init__(self, network):
        super(LogAdapter, self).__init__()
        self.keepListening = False
        self.receivingFile = False
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
                rawData = socket.recv(PPacket.PACKET_SIZE)
                if rawData:
                    Thread(target=self.parseData, args=(rawData,)).start()

    def parseData(self, data):
        packetInput = PPacket.parsePacket(data)
        if not packetInput:
            return
        self.logPacket(packetInput)

        # Accept SYN if not currently in the middle of a transfer
        if not self.receivingFile and packetInput.packetType == PPacketType.SYN:
            self.startReceivingFile(packetInput)

        # Accept DATA if in the middle of a transfer
        elif packetInput.packetType == PPacketType.DATA:
            self.receiveData(packetInput)

        # Accept EOT if in the middle of a transfer
        elif packetInput.packetType == PPacketType.EOT:
            self.receiveEOT(packetInput)

        self.replyAck()

    def startReceivingFile(self, packet):
        self.logSignal.emit("START RECEIVING FILE")
        self.sequenceNumber = 0
        self.receivingFile = True
        self.windowSize = packet.windowSize
        self.sequenceNumber = packet.ackNum

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
        if packet.seqNum - self.sequenceNumber != 1:
            return

        self.sequenceNumber = packet.ackNum
        self.theFile.write(packet.data)

    def receiveEOT(self, packet):
        if packet.seqNum - self.sequenceNumber != 1:
            return

        self.sequenceNumber = packet.ackNum
        self.receivingFile = False
        self.theFile.close()
        self.logSignal.emit("FILE TRANSFER COMPLETE")

    def replyAck(self):
        packetAck = PPacket(PPacketType.ACK, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
        self.logPacket(packetAck)
        self.network.send(packetAck.toBytes())

class Emulator:
    def __init__(self, address, port):
        self.listenHost = ''
        self.listenPort = 7005
        self.client1 = None
        self.client2 = None

        # Setup both Control and Data Sockets
        self.setupSocket(self.listenPort, self.receive)

    def setupSocket(self, port, clientFunc):
        theSocket = socket(AF_INET, SOCK_STREAM)
        theSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Bind Socket
        try:
            theSocket.bind((self.listenHost, port))
            theSocket.listen(5)
        except:
            print("Socket couldn\'t be binded")
            raise

        # Wait for Connection
        while True:
            client, address = theSocket.accept()
            if self.client1 is None:
                self.client1 = client
            elif self.client2 is None:
                self.client2 = client
            else:
                theSocket.close()
                break

            Thread(target = clientFunc, args = (theSocket, client, address)).start()

    def receive(self, theSocket, client, address):
        self.printClients()

        while True:
            rawData = client.recv(PPacket.PACKET_SIZE)

            if not rawData:
                break
            else:
                packet = PPacket.parsePacket(rawData)
                if packet.packetType == PPacketType.DCN:
                    self.removeClient(client)
                    print("Client Disconnected")
                else:
                    # TODO: implement proper bit error rate
                    num = randint(0,1)
                    if num == 1:
                        if client is self.client1:
                            self.client2.send(rawData)
                            print("Client 1 -> Client 2")
                        if client is self.client2:
                            self.client1.send(rawData)
                            print("Client 2 -> Client 1")


    def shutdown(self):
        self.theSocket.shutdown(SHUT_RDWR)
        self.theSocket.close()

    def printClients(self):
        client1 = self.client1.getpeername() if self.client1 != None else None
        client2 = self.client2.getpeername() if self.client2 != None else None
        print("Connected Clients: {}, {}".format(client1, client2))

    def removeClient(self, client):
        if client is self.client1:
            self.client1 = None
        elif client is self.client2:
            self.client2 = None
