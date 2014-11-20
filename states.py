#!/usr/bin/env python3

"""
Dialog states implementation.
"""
__author__ = "Mark Birger"
__date__ = "18 Nov 2014"

from phrase import Phrase

class Question:
    """
    This class implements question state of dialog.
    """
    def __init__(self, phrase, scope):
        self.scope = scope
        self.phrase = Phrase(phrase, self.scope)
        self.childs = []

    def add(self, answer):
        """
        Adds answer to set of answers of this question.
        """
        self.childs.append(answer)

    def compare(self, input_phrase):
        """
        Forwards comparison to phrase.
        """
        return self.phrase.compare(input_phrase)

    def accept(self, input_phrase):
        """
        Triggers when asked this question.
        """
        #TODO: probability processing
        self.phrase.accept(input_phrase)
        tosay = []
        toask = []
        for answer in self.childs:
            answer, questions = answer.accept()
            tosay.append(answer)
            toask.extend(questions)
        return tosay, toask

    def __str__(self):
        return str(self.phrase)

class Answer:
    """
    Class represents answer state of dialog.
    """
    def __init__(self, phrase, scope):
        self.scope = scope
        self.groupid = None
        self.probablity = 100
        phrase = self.parse(phrase)
        self.phrase = Phrase(phrase, self.scope)
        self.childs = []

    def parse(self, phrase):
        """
        Parses probabilities of this answer.
        """
        #TODO: parsing percents at start of phrase
        return phrase

    def add(self, question):
        """
        Adds childs questions to this answer state.
        """
        self.childs.append(question)

    def accept(self):
        """
        Called when this answer triggered.
        """
        self.phrase.accept()
        return str(self.phrase), self.childs

    def __str__(self):
        return str(self.phrase)


class Routine:
    def __init__(self):
        pass

# q1 = Question("How do yo do?")
# a1 = Answer("I'm fine thanx `greetings:True`")
# q1.add(a1)
# print(q1.accept(input("You> ")))