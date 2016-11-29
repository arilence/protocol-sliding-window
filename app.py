"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        app.py - main entry point of the application
--
--      PROGRAM:            file_transport
--
--      FUNCTIONS:          __init__(self)
--                          parseCmdArguments()
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
--      This program is the main entry point for a file transfer program that uses a
--      custom sliding window based transfer protocol. It will run in either Client mode
--      or Server depends on the specified arguments.
--      Specifying a flag --emulator will start the program in server / network emulator
--      mode.
---------------------------------------------------------------------------------------"""
import sys, argparse
from network import *
from gui import *

def parseCmdArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='host ip to bind to', default='')
    parser.add_argument('--port', help='port number to listen on', default=7005, type=int)
    parser.add_argument('--emulator', help='starts up in network emulator mode', action='store_true')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # Parse Input Arguments
    args = parseCmdArguments()

    if (args.emulator):
        window = Application(sys.argv, "C7005 Final Project", True)

    else:
        window = Application(sys.argv, "C7005 Final Project", False)
