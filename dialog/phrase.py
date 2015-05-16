#!/usr/bin/env python3

"""
Phrase processing module.
"""
__author__ = "Mark Birger"
__date__ = "19 Nov 2014"

import re           # for text processin
import ast          # for safe literal evaluation
import dialog.link_parser as link_parser  # for NLP parsing

class Phrase:
    """
    This class implements one phrase (question or answer)
    whith possible manipulation methods. Usage:
    __str__() for evaluating with variables 
    compare() for comparison with input phrase
    accept() to get dictionary of new variables
    """
    def __init__(self, origin, scope):
        self.scope = scope
        self.origin = origin
        self.phrase = origin
        self.substitute = []
        self.setters = []
        self.flexibles = []
        self.requests = []
        self._parse()
        self._validate()
        self.latest = None
        self.parsed = None

    def _parse(self):
        """
        Parses input string using regex.
        """
        pattern = re.compile(r'`([a-zA-Z0-9_]*)((\:|\~|\<)([^`]+))?`')
        for inline in pattern.finditer(self.origin):
            if bool(inline.group(2)):
                if inline.group(3) == ':':
                    self._create_fixed_setter(
                        inline.group(1),
                        inline.group(4),
                        *inline.span())
                elif inline.group(3) == '~':
                    self._create_flexible_setter(
                        inline.group(1),
                        inline.group(4),
                        *inline.span())
                elif inline.group(3) == '<':
                    self._create_routine_request(
                        inline.group(1),
                        inline.group(4),
                        *inline.span())
            else:
                self._create_substition(inline.group(1), *inline.span())
        self._erase_fixed_setters()
        self._erase_flexible_setters()
        self._erase_routine_requests()
        try:
            self.latest = self.evaluate()
            self.parsed = link_parser.parse(self.latest)
            self._link_flexible_setters()
        except KeyError: # not all keys available now
            pass

    def _validate(self):
        """
        Validates, that all charactes in phrase pronouncable.
        """
        # TODO: create phrase validation
        # 1. removes all substitutions
        # 2. checks pronouncable symbol sets
        pass

    def _shift_other(self, shifter, length):
        """
        Shifts all later setter backwards.
        """
        for subs in self.substitute:
            if subs[1] > shifter[3]:
                subs[1] = subs[1] - length
                subs[2] = subs[2] - length
        for fixed_setter in self.setters:
            if fixed_setter[2] > shifter[3]:
                fixed_setter[2] = fixed_setter[2] - length
                fixed_setter[3] = fixed_setter[3] - length
        for next_setter in self.flexibles:
            if next_setter[2] > shifter[3]:
                next_setter[2] = next_setter[2] - length
                next_setter[3] = next_setter[3] - length
        for request in self.requests:
            if request[2] > shifter[3]:
                request[2] = request[2] - length
                request[3] = request[3] - length

    def _create_substition(self, name, pos1, pos2):
        """
        Adds variables substitutions to list.
        """
        self.substitute.append([name, pos1, pos2])

    def _create_fixed_setter(self, name, value, pos1, pos2):
        """
        Adds fixed setters to list.
        """
        self.setters.append([name, value, pos1, pos2])

    def _erase_fixed_setters(self):
        """
        Erase fixed setters from phrase.
        Shifts another setters and substitutions.
        """
        for setter in self.setters:
            length = setter[3] - setter[2]
            self._shift_other(setter, length)
            self.phrase = self.phrase[:setter[2]] + self.phrase[setter[3]:]
    
    def _create_flexible_setter(self, name, word, pos1, pos2):
        """
        Adds flexible setters to list.
        """
        self.flexibles.append([name, word, pos1, pos2, None])

    def _erase_flexible_setters(self):
        """
        Erase flexible setters from phrase.
        Shifts another setters and subnstitutions.
        """
        for setter in self.flexibles:
            length = setter[3] - setter[2] - len(setter[1])
            self._shift_other(setter, length)
            self.phrase = self.phrase[:setter[2]] + setter[1] \
                + self.phrase[setter[3]:]
            setter[3] = setter[3] - length

    def _link_flexible_setters(self):
        """
        Links flexible setter with it parsed token index.
        """
        for setter in self.flexibles:
            # TODO: error with few words same startswith
            for idx, word in enumerate(self.parsed["words"]):
                if word.startswith(setter[1]):
                    setter[4] = idx

    def _create_routine_request(self, name, value, pos1, pos2):
        """
        Adds routine creator to tlist.
        """
        self.requests.append([name, value, pos1, pos2])

    def _erase_routine_requests(self):
        """
        Erases all routines requests. Shifts any other setters.
        """
        for request in self.requests:
            length = request[3] - request[2]
            self._shift_other(request, length)
            self.phrase = self.phrase[:request[2]] + self.phrase[request[3]:]

    def evaluate(self):
        """
        Returns string with all substitutions.
        More acceptable for answers.
        """
        tmp = self.phrase
        offset = 0
        for subs in self.substitute:
            value = str(self.scope.get(subs[0])) #TODO: change globals
            tmp = tmp[:subs[1]+offset] + value + tmp[subs[2]+offset:]
            offset = offset - (subs[2] - subs[1]) + len(value)
        return tmp

    def _update_parsed(self):
        """
        Method evaulates string and if it's changed, 
        parses the new one with link-parser.
        """
        # TODO: probably add check for changed vaules before eval
        try:
            if self.evaluate() != self.latest:
                self.latest = self.evaluate()
                self.parsed = link_parser.parse(self.latest)
                self._link_flexible_setters()
        except KeyError:
            print("WARNING: Can't evaluate")

    def accept(self, input_phrase=None):
        """
        Creates a dictionary of variables to change.
        Used if dialog moves thru this state.
        More acceptable for questions.
        """
        toset = {}
        for setter in self.setters:
            toset[setter[0]] = ast.literal_eval(setter[1])
        if input_phrase is not None:
            self._update_parsed()
            for setter in self.flexibles:
                val = link_parser.extract(setter[4], self.parsed, input_phrase)
                toset[setter[0]] = val
        self.scope.set(toset)
        for request in self.requests:
            self.scope.send(request[0], ast.literal_eval(request[1]))

    def compare(self, input_phrase):
        """
        Compares input phrase with this phrase
        """
        subs_input = link_parser.substitute(input_phrase)
        self._update_parsed()
        subs_self = link_parser.substitute(self.parsed)
        similarity = 0
        for link1 in subs_self:
            for link2 in subs_input:
                if link1 == link2:
                    similarity += 1
        # TODO: understand why it is problem here
        if len(subs_self) != 0:
            similarity = similarity/len(subs_self)
        else:
            similarity = 0
        # rejection of phrase in case of invalid parsing
        rejection = []
        for setter in self.flexibles:
            if link_parser.extract(setter[4], self.parsed, input_phrase) is None:
                rejection = [setter[0]]
                break
        return similarity, rejection

    def __str__(self):
        return self.evaluate()
