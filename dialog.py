#!/usr/bin/env python3

"""
Dialog interperter.
"""
__author__ = "Mark Birger"
__date__ = "19 Nov 2014"

from parser import Parser
from scope import Scope
from returns import Returns
import speech
import link_parser

import multiprocessing

class Dialog:
    """
    Dialog interperter class.
    """
    def __init__(self, scope):
        self.expected = []
        self.scope = Scope(scope)
        self.returns = Returns()

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
