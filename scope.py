#!/usr/bin/env python3

"""
Scope manipulations.
"""
__author__ = "Mark Birger"
__date__ = "20 Nov 2014"

import multiprocessing

class Scope:
    def __init__(self, scope):
        self.scope = {}
        for name, obj in scope.items():
            if not name.startswith('__') and name != "Dialog":
                self.scope[name] = obj

    def get(self, name):
        if hasattr(self.scope[name], '__call__'):
            return self.scope[name]()
        else:
            return self.scope[name]

    def set(self, variables):
        self.scope.update(variables)

    def parallel(self, name, return_queue):
        routine = multiprocessing.Process(
            target=self.scope[name],
            args=(return_queue, ))
        routine.start()
        return routine
