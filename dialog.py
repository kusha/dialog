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
<<<<<<< HEAD
        parser = Parser(filename, self.scope, self.returns)
=======
        """
        Loads dialog from the file.
        Uses Parser module.
        """
        parser = Parser(filename, self.scope)
>>>>>>> FETCH_HEAD
        self.expected.extend(parser.result())

    def _extend_expected(self, quesitons):
         # TODO: more elegant way to extends expected questions
        expected_strings = [str(x) for x in self.expected]
        for new in quesitons:
            if not str(new) in expected_strings:
                print("+\t%s"%(new))
                self.expected.append(new)

    def start(self):
<<<<<<< HEAD
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
        # recognizer.start() # IN CASE OF SPEECH RECOGNITION
        # listener.start()   # IN CASE OF SPEECH RECOGNITION
        occupation.set()
        print("======")
        for state in self.expected:
            print("\t%s" % (state))
        print("======")
        
=======
        """
        Interprets dialog
        """
>>>>>>> FETCH_HEAD
        while True:
            # process routines answers
            answers = self.returns.get_returns()
            for answer in answers:
                tosay, questions = answer.accept()
                speaker_queue.put(tosay)
                print("Bot> "+tosay)
                self._extend_expected(questions)
            # process input
            input_phrase = input("You> ") # IN CASE OF TEXT MODE
            # input_phrase = listener_queue.get() # IN CASE OF SPEECH RECOGNITION
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
<<<<<<< HEAD
            else:
                tosay, questions = state.accept(input_phrase)
                for answer in tosay:
                    if answer != "":
                        speaker_queue.put(answer)
                        print("Bot> "+answer)
                self._extend_expected(questions)
=======

    def listen(self):
        """
        Waiting for user input.
        """
        #TODO: microphone parsing
        return input("You> ")
>>>>>>> FETCH_HEAD
