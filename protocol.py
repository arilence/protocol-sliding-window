from enum import Enum
import base64

class PPacketType(Enum):
    def __str__(self):
        return str(self.value)

    def numToStr(self):
        if self.value == 1:
            return "SYN"
        elif self.value == 2:
            return "ACK"
        elif self.value == 3:
            return "DATA"
        elif self.value == 4:
            return "EOT"

    SYN  = 1
    ACK  = 2
    DATA = 3
    EOT  = 4
    DCN  = 5

class PPacket:
    PACKET_SIZE = 8192
    TYPE_SIZE = 3
    SEQ_SIZE = 12
    WIN_SIZE = 3
    ACK_SIZE = 12
    DATA_SIZE = PACKET_SIZE - TYPE_SIZE - SEQ_SIZE - WIN_SIZE - ACK_SIZE - 4

    def __init__(self, packetType, seqNum, windowSize, ackNum):
        self.packetType = packetType
        self.seqNum = seqNum
        self.windowSize = windowSize
        self.ackNum = ackNum
        self.data = b''

    @staticmethod
    def parsePacket(data):
        values = data.split(b'|', maxsplit=4)
        if len(values) == 4 or len(values) == 5:
            strPacketType = values[0].decode('utf-8')
            strSeqNum = values[1].decode('utf-8')
            strWindowSize = values[2].decode('utf-8')
            strAckNum = values[3].decode('utf-8')

            packetType = PPacketType(int(strPacketType.strip()))
            seqNum = int(strSeqNum.strip())
            windowSize = int(strWindowSize.strip())
            ackNum = int(strAckNum.strip())
            tempPacket = PPacket(packetType, seqNum, windowSize, ackNum)
            if len(values) == 5:
                data = values[4]
                tempPacket.setData(data)
            return tempPacket

        return False

    def setData(self, data):
        self.data = data

    def toBytes(self):
        packetType = "{:<3.3}".format(str(self.packetType.value)).encode('utf-8')
        seqNum = "|{:<12.12}".format(str(self.seqNum)).encode('utf-8')
        windowSize = "|{:<3.3}".format(str(self.windowSize)).encode('utf-8')
        ackNum = "|{:<12.12}|".format(str(self.ackNum)).encode('utf-8')

        if not self.data:
            self.data = b''

        blankBytes = PPacket.DATA_SIZE - len(self.data)
        if blankBytes == 0:
            return packetType + seqNum + windowSize + ackNum + self.data
        else:
            return packetType + seqNum + windowSize + ackNum + self.data + bytearray(blankBytes)

    def __str__(self):
        packetType = "{:<3.3}".format(str(self.packetType.value))
        seqNum = "{:<12.12}".format(str(self.seqNum))
        windowSize = "{:<3.3}".format(str(self.windowSize))
        ackNum = "{:<12.12}".format(str(self.ackNum))
        data = "{:<2014.2014}".format(str(self.data))

        s = ""
        s += packetType + "|"
        s += seqNum + "|"
        s += windowSize + "|"
        s += ackNum + "|"
        s += data
        return s

class PWindow:
    def __init__(self, windowSize):
        pass
