# Initial Variables
windowSize = 6
leftSide = 0
rightSide = 5
usableAddLocation = 0
usableGetLocation = 0


def add
  if usableAddLocation < rightSide
    add packet to array[usableAddLocation]
    usableAddLocation += 1

def get
  return array[usableGetLocation]

def ack
  from leftSide -> usableGetLocation
    if the incoming seqNum == packet in array
      set packet to acked
    if the packet == leftSide
      leftSide += 1
      if rightSide - leftSide < windowSize
        rightSide += 1
