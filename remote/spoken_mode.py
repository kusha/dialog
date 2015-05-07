
__author__ = "Mark Birger"
__date__ = "7 May 2015"
__version__ = "0.3"

import multiprocessing
from dialog import speech

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

occupation = multiprocessing.Event()
listener_queue = multiprocessing.Queue(maxsize=0)
recognizer_queue = multiprocessing.Queue(maxsize=0)
speaker_queue = multiprocessing.Queue(maxsize=0)
speaker = multiprocessing.Process(
    target=speech.speaker,
    args=(occupation, speaker_queue, ))
recognizer = multiprocessing.Process(
    target=speech.recognizer,
    args=(recognizer_queue, listener_queue, ))
listener = multiprocessing.Process(
    target=speech.listener,
    args=(occupation, recognizer_queue, ))
speaker.start()
recognizer.start()
listener.start()
occupation.set()

while True:
    if not listener_queue.empty():
        input_phrase = listener_queue.get()
        # print(input_phrase)
        UDPSock.sendto(input_phrase.encode("utf-8"), addr)
UDPSock.close()
os._exit(0)
