from socket import (
    socket, gethostbyname, gaierror,
    AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_SNDBUF, SHUT_RDWR
)
from threading import Thread
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot, QObject)
from protocol import PWindow, PPacket, PPacketType
from timeit import default_timer
import time, sys, os, collections
import select as fileSelect

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
        self.size = 2048

    def connect(self, address, port):
        self.sockObj = socket(AF_INET, SOCK_STREAM)      # Create a TCP socket object
        self.sockObj.setsockopt(SOL_SOCKET, SO_SNDBUF, self.size)
        self.sockObj.connect((address, port));
        return True

    def disconnect(self):
        message = "killsrv"
        self.sockObj.send(message.encode(ENCODING_TYPE))
        self.sockObj.shutdown(SHUT_RDWR)
        return True

    def send(self, data):
        self.sockObj.send(str(data).encode(ENCODING_TYPE))

    def receive(self):
        return self.sockObj.recv(self.size)

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
        self.currentState = PPacketType.SYN

        # Get the file ready for reading
        theFile = open(fileLocation, 'rb')
        fileSize = os.stat(fileLocation)

        # Setup Thread for sending packets
        Thread(target=self.sendingFileThread, args=(theFile,)).start()

        # Setup Thread for receiving packets
        Thread(target=self.receivingAckThread).start()

    def sendingFileThread(self, theFile):
        # Send all of the file data
        self.slidingWindow = collections.deque()
        self.test_num = 0
        sendTime = default_timer()

        while self.sendingFileData:
            if self.currentState == PPacketType.SYN:
                if self.shouldSend:
                    packetInitial = PPacket(PPacketType.SYN, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
                    self.logPacket(packetInitial)
                    self.network.send(str(packetInitial))
                    sendTime = default_timer()
                    self.shouldSend = False

            elif self.currentState == PPacketType.DATA:
                if len(self.slidingWindow) < self.windowSize and self.test_num < 10:
                    packet = PPacket(PPacketType.DATA, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
                    packet.setData("Hello")
                    self.slidingWindow.append(packet)
                    self.test_num = self.test_num + 1

                elif self.shouldSend:
                    tempSlidingWindow = self.slidingWindow.copy()
                    for index in range(len(tempSlidingWindow)):
                        transferPacket = tempSlidingWindow.popleft()
                        self.logPacket(transferPacket)
                        self.network.send(str(transferPacket))
                    sendTime = default_timer()
                    self.shouldSend = False

            elif self.currentState == PPacketType.EOT:
                if self.shouldSend:
                    packetEot = PPacket(PPacketType.EOT, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
                    self.logPacket(packetEot)
                    self.network.send(str(packetEot))
                    sendTime = default_timer()
                    self.shouldSend = False

            if default_timer() - sendTime >= 2:
                self.shouldSend = True

    def receivingAckThread(self):
        socket = self.network.sockObj
        size = self.network.size

        while self.sendingFileData:
            r, _, _ = fileSelect.select([socket], [], [])
            if r and self.sendingFileData:
                rawData = self.network.receive()
                data = rawData.decode(ENCODING_TYPE)
                if data:
                    packetResponse = PPacket.parsePacket(data)
                    if not packetResponse:
                        return
                    self.logPacket(packetResponse)

                    if packetResponse.seqNum == self.sequenceNumber + 1 and packetResponse.packetType == PPacketType.ACK:
                        if self.currentState == PPacketType.SYN:
                            self.currentState = PPacketType.DATA
                            self.shouldSend = True
                            self.sequenceNumber = packetResponse.ackNum
                        elif self.currentState == PPacketType.DATA:
                            if self.test_num == 10:
                                self.currentState = PPacketType.EOT

                            diff = packetResponse.seqNum - self.sequenceNumber
                            for num in range(0, diff):
                                self.slidingWindow.popleft()
                            self.sequenceNumber = packetResponse.ackNum
                            self.shouldSend = True

                        elif self.currentState == PPacketType.EOT:
                            self.logSignal.emit("FILE TRANFER COMPLETE")
                            self.sendingFileData = False

class Receiver(LogAdapter):
    def __init__(self, network):
        super(LogAdapter, self).__init__()
        self.keepListening = False
        self.receivingFile = False
        self.network = network

    def start(self):
        self.keepListening = True
        Thread(target=self.waitForSocket).start()

    def pause(self):
        self.keepListening = False

    def waitForSocket(self):
        socket = self.network.sockObj
        size = self.network.size

        while self.keepListening:
            r, _, _ = fileSelect.select([socket], [], [])
            if r and self.keepListening:
                # ready to receive
                rawData = socket.recv(size)
                data = rawData.decode(ENCODING_TYPE)
                if data:
                    Thread(target=self.parseData, args=(data,)).start()

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
        self.theFile = open("thefile.txt", 'wb')

    def receiveData(self, packet):
        if packet.seqNum - self.sequenceNumber != 1:
            return

        self.sequenceNumber = packet.ackNum
        # TODO: save data to the file on disk
        #data = packet.data.decode(ENCODING_TYPE)
        #self.theFile.write(packet.data)

    def receiveEOT(self, packet):
        if packet.seqNum - self.sequenceNumber != 1:
            return

        self.sequenceNumber = packet.ackNum
        self.receivingFile = False
        self.logSignal.emit("FILE TRANSFER COMPLETE")
        self.theFile.close()

    def replyAck(self):
        packetAck = PPacket(PPacketType.ACK, self.sequenceNumber, self.windowSize, self.sequenceNumber + 1)
        self.logPacket(packetAck)
        self.network.send(str(packetAck))

class Emulator:
    def __init__(self, address, port):
        self.listenHost = ''
        self.listenPort = 7005
        self.size = 2048
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
            rawData = client.recv(self.size)

            if not rawData:
                break
            else:
                data = rawData.decode(ENCODING_TYPE)
                if data == 'killsrv':
                    self.removeClient(client)
                    print("Client Disconnected")
                else:
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
