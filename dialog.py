#!/usr/bin/env python3

"""
Dialog interperter.
"""
__author__ = "Mark Birger"
__date__ = "19 Nov 2014"

from parser import Parser
from scope import Scope

class Dialog:
    """
    Dialog interperter class.
    """
    def __init__(self, scope):
        self.expected = []
        self.scope = Scope(scope)

    def load(self, filename):
        """
        Loads dialog from the file.
        Uses Parser module.
        """
        parser = Parser(filename, self.scope)
        self.expected.extend(parser.result())

    def start(self):
        """
        Interprets dialog
        """
        while True:
            input_phrase = self.listen()
            for state in self.expected:
                if state.compare(input_phrase):
                    tosay, toask = state.accept(input_phrase)
                    for answer in tosay:
                        print("Bot> "+answer)
                    self.expected.extend(toask)
                    break
            else:
                print("Bot> ???")

    def listen(self):
        """
        Waiting for user input.
        """
        #TODO: microphone parsing
        return input("You> ")
