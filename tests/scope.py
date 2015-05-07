#!/usr/bin/env python3

"""
Fake scope module for testing.
Imitiates scope object, which
conains varaibles and function 
for evaluation.
"""
__author__ = "Mark Birger"
__date__ = "4 Apr 2015"

class Scope:

    def __init__(self):
        self.value = 0
        self.raise_error_flag = False
        self.changeable = True

        self.toset = {}
        self.tosend = {}

    def set(self, toset):
        self.toset = toset

    def send(self, routine, value):
        self.tosend[routine] = value

    def get(self, name):
        if name == "undefined_var":
            raise KeyError
        elif name == "iteratable":
            self.value += 1
            return self.value
        elif name == "changeable":
            if self.raise_error_flag:
                raise KeyError
            else:
                return self.changeable
        else:
            return "value"

    def change(self):
        """
        Used in test_update_parsed.
        """
        self.changeable = not self.changeable

    def raise_error(self):
        """
        Used in test_update_parsed.
        """
        raise_error_flag = True