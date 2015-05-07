
__author__ = "Mark Birger"
__date__ = "7 May 2015"
__version__ = "0.3"

import os
from socket import *
import argparse
import signal
import sys

def interrupt_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, interrupt_handler)

def postitive_int(value):
    int_ivalue = int(value)
    if int_ivalue < 0:
        raise argparse.ArgumentTypeError("%s is not positive int value" % value)
    return int_ivalue

parser = argparse.ArgumentParser(
    description=__doc__,
    epilog=__author__+" "+__date__)
parser.add_argument(
    '--version',
    action='version',
    version='%(prog)s '+__version__)
parser.add_argument(
    '-p',
    '--port',
    action='store',
    type=postitive_int,
    required=False, 
    default="42424",
    help='UDP server port',
    dest='port')
parser.add_argument(
    'server',
    action='store',
    help='server hostname/ip', 
    metavar='SERVER')
options = parser.parse_args()

addr = (options.server, options.port)
UDPSock = socket(AF_INET, SOCK_DGRAM)

while True:
    UDPSock.sendto(input("You> ").encode("utf-8"), addr)
UDPSock.close()
os._exit(0)
