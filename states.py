#!/usr/bin/env python3

"""
Dialog states implementation.
"""
__author__ = "Mark Birger"
__date__ = "18 Nov 2014"

from phrase import Phrase
import multiprocessing
import ast

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
    def __init__(self, call_line, scope, returns):
        self.scope = scope
        self.name = call_line[1:-2]
        self.childs = []
        self.returns = returns

    def add(self, literal):
        self.childs.append(literal)

    def accept(self):
        # get possible returns
        cases = [literal.accept() for literal in self.childs]
        literals, answers = zip(*cases)
        literals = list(literals)
        answers = [x[0] for x in list(answers)]
        # create return way
        return_queue = self.returns.new_return(answers)
        # call routine handler
        def routine_handler(scope, literals, return_queue):
            # create routine process
            proc_queue = multiprocessing.Queue(maxsize=0)
            process = scope.parallel(self.name, proc_queue)
            # start monitoring
            while process.is_alive():
                if not proc_queue.empty():
                    result = proc_queue.get()
                    for idx, case in enumerate(literals):
                        if case == result:
                            return_queue.put(idx)
        handler = multiprocessing.Process(
            target=routine_handler,
            args=(self.scope, literals, return_queue, ))
        handler.start()
        return "", []

    def __str__(self):
        # TODO: remove this method if it's not called
        print("WARNING")
        return ""

class Literal:
    def __init__(self, value):
        self.value = ast.literal_eval(value)
        self.childs = []

    def add(self, answer):
        self.childs.append(answer)

    def accept(self):
        # for really, it's pre-accept
        return self.value, self.childs

# q1 = Question("How do yo do?")
# a1 = Answer("I'm fine thanx `greetings:True`")
# q1.add(a1)
# print(q1.accept(input("You> ")))