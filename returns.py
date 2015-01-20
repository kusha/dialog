#!/usr/bin/env python3

"""
Return answers implementation.
"""
__author__ = "Mark Birger"
__date__ = "20 Jan 2015"

import multiprocessing

class Returns:
    def __init__(self):
        self.routines = []

    def new_return(self, answers):
        routine = {}
        routine["answers"] = answers
        routine["queue"] = multiprocessing.Queue(maxsize=0)
        self.routines.append(routine)
        return routine["queue"]

    def get_returns(self):
        answers = []
        for routine in self.routines:
            while not routine["queue"].empty():
                answer_idx = routine["queue"].get()
                answers.append(routine["answers"][answer_idx])
        return answers