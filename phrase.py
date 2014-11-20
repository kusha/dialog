#!/usr/bin/env python3

"""
Phrase processing module.
"""
__author__ = "Mark Birger"
__date__ = "19 Nov 2014"

import re, ast

class Phrase:
    """
    This class implements one phrase (question or answer)
    whith possible manipulation methods. Usage:
    __str__ for evaluating with variables 
    compare for comparison with input phrase
    accept to get dictionary of new variables
    """
    def __init__(self, origin, scope):
        self.scope = scope
        self.origin = origin
        self.phrase = origin
        self.substitute = []
        self.setters = []
        self.flexibles = []
        self.parse()
        self.validate()

    def parse(self):
        """
        Parses input string using regex.
        """
        pattern = re.compile(r'`([a-zA-Z0-9_]*)((\:|\~)([^`]+))?`')
        for inline in pattern.finditer(self.origin):
            if bool(inline.group(2)):
                if inline.group(3) == ':':
                    self.create_fixed_setter(
                        inline.group(1),
                        inline.group(4),
                        *inline.span())
                elif inline.group(3) == '~':
                    self.create_flexible_setter(
                        inline.group(1),
                        inline.group(4),
                        *inline.span())
            else:
                self.create_substition(inline.group(1), *inline.span()) 
            # (name, existence, relation, value)
            # print(name, existence, relation, value)  
        self.erase_fixed_setters()
        self.erase_flexible_setters()

    def validate(self):
        """
        Validates, that all charactes in phrase pronouncable.
        """
        #TODO: create phrase validation
        # 1. removes all substitutions
        # 2. checks pronouncable symbol sets
        pass

    def create_substition(self, name, pos1, pos2):
        """
        Adds variables substitutions to list.
        """
        self.substitute.append([name, pos1, pos2])

    def create_fixed_setter(self, name, value, pos1, pos2):
        """
        Adds fixed setters to list.
        """
        self.setters.append([name, value, pos1, pos2])

    def erase_fixed_setters(self):
        """
        Erase fixed setters from phrase.
        Shifts another setters and subnstitutions.
        """
        for setter in self.setters:
            length = setter[3] - setter[2]
            for subs in self.substitute:
                if subs[1] > setter[3]:
                    subs[1] = subs[1] - length
                    subs[2] = subs[2] - length
            for next_setter in self.setters:
                if next_setter[2] > setter[3]:
                    next_setter[2] = next_setter[2] - length
                    next_setter[3] = next_setter[3] - length
            for flex_setter in self.flexibles:
                if flex_setter[2] > setter[3]:
                    flex_setter[2] = flex_setter[2] - length
                    flex_setter[3] = flex_setter[3] - length
            self.phrase = self.phrase[:setter[2]] + self.phrase[setter[3]:]
    
    def create_flexible_setter(self, name, word, pos1, pos2):
        """
        Adds flexible setters to list.
        """
        self.flexibles.append([name, word, pos1, pos2])

    def erase_flexible_setters(self):
        """
        Erase flexible setters from phrase.
        Shifts another setters and subnstitutions.
        """
        for setter in self.flexibles:
            length = setter[3] - setter[2] - len(setter[1])
            for subs in self.substitute:
                if subs[1] > setter[3]:
                    subs[1] = subs[1] - length
                    subs[2] = subs[2] - length
            for fixed_setter in self.setters:
                if fixed_setter[2] > setter[3]:
                    fixed_setter[2] = fixed_setter[2] - length
                    fixed_setter[3] = fixed_setter[3] - length
            for next_setter in self.flexibles:
                if next_setter[2] > setter[3]:
                    next_setter[2] = next_setter[2] - length
                    next_setter[3] = next_setter[3] - length
            self.phrase = self.phrase[:setter[2]] + setter[1] \
                + self.phrase[setter[3]:]
            setter[3] = setter[3] - length

    def evaluate(self):
        """
        Returns string with all substitutions.
        """
        tmp = self.phrase
        offset = 0
        for subs in self.substitute:
            value = str(self.scope.get(subs[0])) #TODO: change globals
            tmp = tmp[:subs[1]+offset] + value + tmp[subs[2]+offset:]
            offset = offset - (subs[2] - subs[1]) + len(value)
        return tmp

    def accept(self, input_phrase=None):
        """
        Creates a dictionary of variables to change.
        Used if dialog moves thru this state.
        """
        toset = {}
        for setter in self.setters:
            toset[setter[0]] = ast.literal_eval(setter[1])
        if input_phrase is not None:
            pass #TODO: flexible parsing
        self.scope.set(toset)

    def compare(self, input_phrase):
        """
        Compares input phrase with this phrase
        """
        #TODO: abssolute comparison value
        return self.evaluate() == input_phrase

    def __str__(self):
        return self.evaluate()

# btc_rate = 400
# cpu_temp = 45
# okaa = "pampam"

# phrase = Phrase("It's `btc_rate` euros for one bitcoin `cpu_temp` `variable_toset:\"literal\"` `friendly:False` gghhg `okaa` `variable_name~word` lol")
# print(phrase)
# print(phrase.evaluate())
# print(phrase.accept())
# print(phrase.compare("It's 400 euros for one bitcoin 45   gghhg pampam word lol"))

# OUTPUT:

# It's `btc_rate` euros for one bitcoin `cpu_temp`   gghhg `okaa`
# word
#  lol
# It's `btc_rate` euros for one bitcoin `cpu_temp`   gghhg `okaa` word lol
# [['btc_rate', 5, 15], ['cpu_temp', 38, 48], ['okaa', 57, 63]]
# [['variable_toset', '"literal"', 49, 75], ['friendly', 'False', 50, 66]]
# [['variable_name', 'word', 64, 68]]
# It's 400 euros for one bitcoin 45   gghhg pampam word lol
# It's 400 euros for one bitcoin 45   gghhg pampam word lol
# {'friendly': False, 'variable_toset': 'literal'}
# True
