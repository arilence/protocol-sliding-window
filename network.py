from socket import (
    socket, gethostbyname, gaierror,
    AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_SNDBUF, SHUT_RDWR
)
from threading import Thread
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot, QObject)
from protocol import PWindow, PPacket, PPacketType
import time, sys, os
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
        Thread(target=self.send, args=(fileLocation,)).start()
        return True

    def send(self, fileLocation):
        window = PWindow(7)         # Start with a smallish window size
        self.sequenceNumber = 0
        self.startingSeqNum = 0
        self.currentState = "SYN"

        # Get the file ready for reading
        theFile = open(fileLocation, 'rb')
        fileSize = os.stat(fileLocation)

        # Setup Thread for sending packets
        Thread(target=self.sendingFileThread, args=(theFile,)).start()

        # Setup Thread for receiving packets
        Thread(target=self.receivingAckThread).start()

    def sendingFileThread(self, theFile):
        if self.currentState == "SYN":
            # Send packet to initiate file transfer
            packetInitial = PPacket(PPacketType.SYN, self.startingSeqNum, 7, self.startingSeqNum + 1)
            self.network.send(str(packetInitial))
        if self.currentStart == "DATA":
            l = theFile.read(PPacket.DATA_SIZE)
            while (l):
                dataPacket = PPacket(PPacketType.DATA,
                                     packetResponse.ackNum,
                                     7,
                                     packetResponse.ackNum + 1)
                dataPacket.setData(str(l, ENCODING_TYPE))
                self.network.send(str(dataPacket))
                l = theFile.read(PPacket.DATA_SIZE)

            packetInitial = PPacket(PPacketType.EOT, 1, 7, 2)
            self.network.send(str(packetInitial))
        if self.currentState == "EOF":
            self.resetFileTransfer()
            self.logSignal.emit("FILE TRANSFER COMPLETE")

    def receivingAckThread(self):
        while True:
            rawData = self.network.receive()
            data = rawData.decode(ENCODING_TYPE)
            packetResponse = PPacket.parsePacket(data)
            if not packetResponse:
                return
            self.logPacket(packetResponse)

            if packetResponse.packetType == PPacketType.ACK and packetResponse.seqNum == self.startingSeqNum + 1:
                if self.currentState == "SYN":
                    self.currentState == "DATA"
                elif self.currentState == "DATA":
                    self.currentState == "EOF"

    def resetFileTransfer(self):
        self.sequenceNumber = 0

class Receiver(LogAdapter):
    def __init__(self, network):
        super(LogAdapter, self).__init__()
        self.keepListening = False
        self.receivingFile = False
        self.theFile = None
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

        # Deal with packet type
        if packetInput.packetType == PPacketType.SYN:
            self.logSignal.emit("START RECEIVING FILE")
            self.startReceivingFile(packetInput)
        elif packetInput.packetType == PPacketType.ACK:
            print("Package Type: ACK")
            # TODO: dafuq? error!
        elif packetInput.packetType == PPacketType.DATA:
            self.receiveData(packetInput)
        elif packetInput.packetType == PPacketType.EOT:
            self.receiveEOT(packetInput)

        # Send ACK back
        ackNum = packetInput.ackNum
        windowSize = packetInput.windowSize
        packetAck = PPacket(PPacketType.ACK, ackNum, windowSize, ackNum+1)
        self.network.send(str(packetAck))

    def resetFileTransfer(self):
        self.receivingFile = False
        self.theFile = None
        self.curSequenceNumber = 0

    def startReceivingFile(self, packet):
        if not self.receivingFile:
            self.receivingFile = True
            self.theFile = open("thefile.txt", 'wb')
            self.curSequenceNumber = packet.seqNum
        else:
            # hmm... a new file is trying to be transferred
            pass

    def receiveData(self, packet):
        # Make sure we receive data in the correct order
        if packet.seqNum == self.curSequenceNumber + 1:
            data = packet.data.decode(ENCODING_TYPE)
            self.theFile.write(data)

    def receiveEOT(self, packet):
        # Make sure we receive data in the correct order
        if packet.seqNum == self.curSequenceNumber + 1:
            self.theFile.close()
            self.resetFileTransfer()
            self.logSignal.emit("FILE TRANSFER COMPLETE")

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
