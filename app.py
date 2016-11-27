import sys, argparse
from network import *
from gui import *

def parseCmdArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='host ip to bind to', default='')
    parser.add_argument('--port', help='port number to listen on', default=7005, type=int)
    parser.add_argument('--receiver', help='starts up in receiver mode', action='store_true')
    parser.add_argument('--emulator', help='starts up in network emulator mode', action='store_true')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # Parse Input Arguments
    args = parseCmdArguments()

    if (args.emulator):
        emulator = Emulator(args.ip, args.port)

    else:
        window = Application(sys.argv, "C7005 Final Project")
        #transmitter = Transmitter(args.ip, args.port)
