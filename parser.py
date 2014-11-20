#!/usr/bin/env python3

"""
Dialog parsing module.
"""
__author__ = "Mark Birger"
__date__ = "19 Nov 2014"

import re
from states import Question, Answer

class Parser:
    def __init__(self, filename, scope, identation='\t'):
        self.scope = scope
        self.identation = identation
        with open(filename) as dialog_file:
            self.lines = dialog_file.read().splitlines()
        self.remove_comments()
        self.remove_whitespaces()
        self.remove_empty_lines()
        self.join_lines()
        self.root = []
        self.stack = []
        self.parse()

    def remove_comments(self):
        self.lines = [re.sub(r'#.*$', '', line) for line in self.lines]

    def remove_whitespaces(self):
        self.lines = [re.sub(r'\s*$', '', line) for line in self.lines]

    def remove_empty_lines(self):
        self.lines = [line for line in self.lines if line != '']

    def join_lines(self):
        joined = []
        summary = ""
        for line in self.lines:
            if line.endswith("\\"):
                if summary == "":
                    summary += line[:-1]
                else:
                    summary += line.lstrip()[:-1]
            else:
                if summary == "":
                    joined.append(line)
                else:
                    joined.append(summary + line.lstrip())
                    summary = ""
        self.lines = joined

    def parse_identations(self, line):
        level = 0
        while line.startswith(self.identation):
            level += 1
            line = line[len(self.identation):]
        return level, line

    def parse(self):
        for line in self.lines:
            level, line = self.parse_identations(line)
            #TODO: routine parsing
            if level % 2 == 0: # it's a question
                new = Question(line, self.scope)
            else:
                new = Answer(line, self.scope)
            self.place_state(level, new)

    def place_state(self, level, state):
        self.stack = self.stack[:level]
        if not self.stack: # we are at the root
            self.root.append(state)
            self.stack.append(state)
        else:
            self.stack[-1].add(state)
            self.stack.append(state)

    def result(self):
        return self.root

# dlg = Parser("examples/tickets.dlg")














