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
        self.processes = {}

    def new_return(self, answers):
        """
        Creates Queue, adds it to the pool.
        """
        routine = {}
        routine["answers"] = answers
        routine["queue"] = multiprocessing.Queue(maxsize=0)
        self.routines.append(routine)
        return routine["queue"]

    def get_returns(self):
        """
        For each routine, get indexes of returns.
        Reuturns every "return" statements.
        """
        answers = []
        for routine in self.routines:
            while not routine["queue"].empty():
                answer_idx = routine["queue"].get()
                answers.append(routine["answers"][answer_idx])
        to_delete = []
        for name, routine in self.processes.items():
            if routine["process"].is_alive():
                while not routine["responses_queue"].empty():
                    response = routine["responses_queue"].get()
                    for idx, case in enumerate(routine["cases"][0]):
                        if case == response:
                            answers.append(routine["cases"][1][idx])
            else:
                # TODO: check how it is safety from his child states
                to_delete.append(name)
        for each in to_delete:
            del self.processes[each]
        return answers


    def new_routine(self, process, name, requests_queue, responses):
        self.processes[name] = {
            "process": process,
            "requests_queue": requests_queue, #TODO: remove, unused, realised with Scope module
            "cases": responses[0],
            "responses_queue": responses[1],
        }
