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

class PPacket:
    TYPE_SIZE = 3
    SEQ_SIZE = 12
    WIN_SIZE = 3
    ACK_SIZE = 12
    DATA_SIZE = 2014

    def __init__(self, packetType, seqNum, windowSize, ackNum):
        self.packetType = packetType
        self.seqNum = seqNum
        self.windowSize = windowSize
        self.ackNum = ackNum
        self.acked = False
        self.data = ""

    @staticmethod
    def parsePacket(data):
        values = data.split('|')
        if len(values) == 4 or len(values) == 5:
            packetType = PPacketType(int(values[0].strip()))
            seqNum = int(values[1].strip())
            windowSize = int(values[2].strip())
            ackNum = int(values[3].strip())
            tempPacket = PPacket(packetType, seqNum, windowSize, ackNum)
            if len(values) == 5:
                data = values[4]
                tempPacket.setData(data)
            return tempPacket

        return False

    def setData(self, data):
        #bytesConverted = base64.b64encode(data)
        self.data = data

    def setAcked(self):
        self.acked = True

    def __str__(self):
        packetType = "{:<3.3}".format(str(self.packetType.value))
        seqNum = "{:<12.12}".format(str(self.seqNum))
        windowSize = "{:<3.3}".format(str(self.windowSize))
        ackNum = "{:<12.12}".format(str(self.ackNum))
        data = "{:<2014.2014}".format(str(self.data))

        s = ""
        s += packetType + "|"                           # MAX:    3 Characters
        s += seqNum + "|"                               # MAX:    4 Characters
        s += windowSize + "|"                           # MAX:    3 Characters
        s += ackNum + "|"                               # MAX:    4 Characters
        s += data                                       # MAX: 2014 Characters
        return s

class PWindow:
    def __init__(self, windowSize):
        pass
