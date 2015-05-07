#!/usr/bin/env python3

"""
Dialog interperter.
"""
__author__ = "Mark Birger"
__date__ = "19 Nov 2014"
__version__ = "0.3"


from dialog import STORAGEPATH
from dialog.parser import Parser
from dialog.scope import Scope
from dialog.returns import Returns
import dialog.speech as speech
import dialog.link_parser as link_parser

import multiprocessing
# import sys
import argparse
import os
import signal
import sys
from socket import *

# USE_EVAL = False
# TTS = "att"

class Dialog:
    """
    Dialog interperter class.
    """
    def __init__(self, scope, storage="./"):

        global STORAGEPATH
        STORAGEPATH = storage + STORAGEPATH
        STORAGEPATH = os.path.abspath(STORAGEPATH)
        print("Data storage path:", STORAGEPATH)
        if not os.path.exists(STORAGEPATH):
            os.makedirs(STORAGEPATH)
        if not os.path.exists(STORAGEPATH + "/answers/"):
            os.makedirs(STORAGEPATH + "/answers/")
        if not os.path.exists(STORAGEPATH + "/questions/"):
            os.makedirs(STORAGEPATH + "/questions/")

        self.expected = []
        self.scope = Scope(scope)
        self.returns = Returns()
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def load(self, filename):
        """
        Loads dialog from the file.
        Uses Parser module.
        """
        parser = Parser(filename, self.scope, self.returns)
        self.expected.extend(parser.result())

    def _extend_expected(self, quesitons):
        """
        Method extends set of expected phrases.
        """
        # TODO: more elegant way to extends expected questions
        expected_strings = [str(x) for x in self.expected]
        for new in quesitons:
            if not str(new) in expected_strings:
                print("+\t%s"%(new))
                self.expected.append(new)

    def start(self):
        """
        Text/spoken mode select method.
        """
        if self.options["is_spoken"] != None:
            if self.options["is_spoken"]:
                return self.start_spoken()
            else:
                return self.start_text()
        else:
            print("Dialog system started in text mode by deafult.")
            print("Use -s option to run spoken mode.")
            return self.start_text()

    def start_spoken(self):
        """
        Interprets dialog with natural speech.
        """
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
        print("======")
        for state in self.expected:
            print("\t%s" % (state))
        print("======")
        while True:
            # process routines answers
            answers = self.returns.get_returns()
            for answer in answers:
                tosay, questions = answer.accept()
                speaker_queue.put(tosay)
                print("Bot> "+tosay)
                self._extend_expected(questions)
            # process input
            if not listener_queue.empty():
                input_phrase = listener_queue.get()
                input_phrase = link_parser.parse(input_phrase)
                states_probability = []
                for state in self.expected:
                    # print(state, state.compare(input_phrase))
                    states_probability.append((state, state.compare(input_phrase)))
                states_probability = sorted(states_probability, key=lambda x: x[1], reverse=True)
                print("======")
                for state in states_probability:
                    print("%.2f\t%s" % (state[1], state[0]))
                print("======")
                state = states_probability[0][0]
                if states_probability[0][1] < 0.2:
                    print("Bot> ???")
                else:
                    tosay, questions = state.accept(input_phrase)
                    for answer in tosay:
                        if answer != "":
                            speaker_queue.put(answer)
                            print("Bot> "+answer)
                    self._extend_expected(questions)

    def start_text(self):
        """
        Interprets dialog in text mode.
        """
        print("======")
        for state in self.expected:
            print("\t%s" % (state))
        print("======")
        while True:
            # process routines answers
            answers = self.returns.get_returns()
            for answer in answers:
                tosay, questions = answer.accept()
                print("Bot> "+tosay)
                self._extend_expected(questions)
            # process input
            input_phrase = input("You> ")
            while not input_phrase.strip():
                print("Empty input string")
                input_phrase = input("You> ")
            input_phrase = link_parser.parse(input_phrase)
            states_probability = []
            for state in self.expected:
                # print(state, state.compare(input_phrase))
                states_probability.append((state, state.compare(input_phrase)))
            states_probability = sorted(states_probability, key=lambda x: x[1], reverse=True)
            print("======")
            for state in states_probability:
                print("%.2f\t%s" % (state[1], state[0]))
            print("======")
            state = states_probability[0][0]
            if states_probability[0][1] < 0.2:
                print("Bot> ???")
            else:
                tosay, questions = state.accept(input_phrase)
                for answer in tosay:
                    if answer != "":
                        print("Bot> "+answer)
                self._extend_expected(questions)

    def start_socket(self, port=42424):
        """
        Listens socket for input phrases.
        """
        host = ""
        buf = 1024
        addr = (host, port)
        UDPSock = socket(AF_INET, SOCK_DGRAM)
        UDPSock.bind(addr)
        print("Listening socket")

        occupation = multiprocessing.Event()
        # listener_queue = multiprocessing.Queue(maxsize=0)
        # recognizer_queue = multiprocessing.Queue(maxsize=0)
        speaker_queue = multiprocessing.Queue(maxsize=0)
        speaker = multiprocessing.Process(
            target=speech.speaker,
            args=(occupation, speaker_queue, ))
        # recognizer = multiprocessing.Process(
        #     target=speech.recognizer,
        #     args=(recognizer_queue, listener_queue, ))
        # listener = multiprocessing.Process(
        #     target=speech.listener,
        #     args=(occupation, recognizer_queue, ))
        speaker.start()
        # recognizer.start()
        # listener.start()
        occupation.set()

        print("======")
        for state in self.expected:
            print("\t%s" % (state))
        print("======")
        while True:
            # process routines answers
            answers = self.returns.get_returns()
            for answer in answers:
                tosay, questions = answer.accept()
                speaker_queue.put(tosay)
                print("Bot> "+tosay)
                self._extend_expected(questions)
            # process input
            (data, addr) = UDPSock.recvfrom(buf)
            input_phrase = data.decode("utf-8")
            print("You> "+input_phrase)
            while not input_phrase.strip():
                print("Empty input string")
                input_phrase = input("You> ")
            input_phrase = link_parser.parse(input_phrase)
            states_probability = []
            for state in self.expected:
                # print(state, state.compare(input_phrase))
                states_probability.append((state, state.compare(input_phrase)))
            states_probability = sorted(states_probability, key=lambda x: x[1], reverse=True)
            print("======")
            for state in states_probability:
                print("%.2f\t%s" % (state[1], state[0]))
            print("======")
            state = states_probability[0][0]
            if states_probability[0][1] < 0.2:
                print("Bot> ???")
            else:
                tosay, questions = state.accept(input_phrase)
                for answer in tosay:
                    if answer != "":
                        speaker_queue.put(answer)
                        print("Bot> "+answer)
                self._extend_expected(questions)
        UDPSock.close()

    @staticmethod
    def interrupt_handler(signal, frame):
        print("INFO: dialog system process is closed")
        sys.exit(0)

def handle(callbacks, before=lambda scope: None, after=lambda scope: None):
    """
    Decorator wrapper, which wraps duplex routine.
    Recives decorator params (callbacks).
    """
    def decorator(async_func):
        """
        Decorator, which recieves duplex routine function.
        """
        def inner(requests, responses, global_scope):
            """
            Resulting function, with changed behavior.
            Called by dialog system.
            """
            initial_scope = {}
            for name, obj in global_scope.items():
                if not name.startswith('__'):
                    initial_scope[name] = obj
            scope = type('', (), initial_scope)()
            before(scope)
            while True:
                while not requests.empty():
                    request = requests.get()
                    if request in callbacks:
                        callbacks[request](scope)
                    else:
                        print("Warining: unhandled request")
                        if "" in callbacks:
                            callbacks[""](scope)
                        else:
                            pass
                # TODO: is it good way to finish routine?
                if hasattr(scope, '_exit') and scope._exit:
                    break
                async_func(requests, responses, scope)
                if hasattr(scope, '_exit') and scope._exit:
                    break
            after(scope)
        return inner
    return decorator

def run_master():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=__author__+" "+__date__)
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s '+__version__)
    parser.add_argument(
        '-s',
        '--spoken', 
        action='store_true',
        required=False, 
        help='run as a spoken dialog system',
        dest='is_spoken')
    self.options = vars(parser.parse_args())
    # print(self.options)
    print("TODO run master mode")

if __name__ == "__main__":
    run_master()

    