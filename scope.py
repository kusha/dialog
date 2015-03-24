#!/usr/bin/env python3

"""
Scope manipulations.
"""
__author__ = "Mark Birger"
__date__ = "20 Nov 2014"

import multiprocessing

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
        self.routines = {}

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

    def parallel(self, name, return_queue):
        """
        Calls simplex routine, asynchroniously.
        """
        routine = multiprocessing.Process(
            target=self.scope[name],
            args=(return_queue, ))
        routine.start()
        return routine

    def parallel2(self, name, requests_queue, return_queue):
        """
        Calls duplex routine, asynchroniously.
        """
        routine = multiprocessing.Process(
            target=self.scope[name],
            args=(requests_queue, return_queue, self.scope, ))
        routine.start()
        self.routines[name] = {
            "process" : routine,
            "requests": requests_queue, 
        }
        return routine

    def send(self, name, value):
        """
        Send value to existing duplex routine.
        """
        to_delete = []
        if name in self.routines:
            if self.routines[name]["process"].is_alive():
                self.routines[name]["requests"].put(value)
            else:
                to_delete.append(name)
        else:
            pass
            #TODO: create error raising
        for each in to_delete:
            del self.processes[each]
