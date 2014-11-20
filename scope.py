#!/usr/bin/env python3

"""
Scope manipulations.
"""
__author__ = "Mark Birger"
__date__ = "20 Nov 2014"

class Scope:
    """
    Class represents objects scope.
    Visible in dialog.
    """
    def __init__(self, scope):
        self.scope = {}
        for name, obj in scope.items():
            if not name.startswith('__') and name != "Dialog":
                self.scope[name] = obj

    def get(self, name):
        """
        Calls inline function or return variables.
        """
        if hasattr(self.scope[name], '__call__'):
            return self.scope[name]()
        else:
            return self.scope[name]

    def set(self, variables):
        """
        Set ups new variables from dictionary.
        """
        self.scope.update(variables)
