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
    """
    Class represents simplex routine call state.
    """
    def __init__(self, call_line, scope, returns):
        self.scope = scope
        self.name = call_line[1:-2]
        self.childs = []
        self.returns = returns

    def add(self, literal):
        """
        Adds response literal.
        """
        self.childs.append(literal)

    def accept(self):
        """
        Method runs new routine in another process.
        """
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

    # def __str__(self):
    #     # TODO: remove this method if it's not called
    #     print("WARNING")
    #     return ""

class Routine2:
    """
    Class implements duplex routine state.
    """
    def __init__(self, call_line, scope, returns):
        self.scope = scope
        self.name = call_line[1:-3]
        self.quesions = [] # question childs
        self.literals = [] # literal childs
        self.returns = returns

    def add(self, state):
        """
        Adds child literals or questions.
        """
        # incase of Routine2 sorting content
        if isinstance(state, Question):
            self.quesions.append(state)
        elif isinstance(state, Literal2):
            self.literals.append(state)
            
    def accept(self):
        """
        Method runs new duplex routine in another process.
        """
        # get possible returns
        cases = [literal.accept() for literal in self.literals]
        literals, answers = zip(*cases)
        literals = list(literals)
        answers = [x[0] for x in list(answers)]
        cases = [literals, answers]
        # initialize i/o queues
        requests_queue = multiprocessing.Queue(maxsize=0)
        responses_queue = multiprocessing.Queue(maxsize=0)
        process = self.scope.parallel2(self.name, \
            requests_queue, responses_queue)
        # register routine
        self.returns.new_routine(process, self.name, \
            requests_queue, (cases, responses_queue))
        # return childs questions
        return "", self.quesions

class Literal:
    """
    This class implements literal state.
    Used as routine child.
    """
    def __init__(self, value):
        self.value = ast.literal_eval(value)
        self.childs = []

    def add(self, answer):
        """
        Answer is spoken at the routine callback.
        Adds answer to the literal childs set.
        """
        self.childs.append(answer)

    def accept(self):
        """
        Returns literal with it's childs.
        Called at routine start, monitored by returns module.
        """
        # for really, it's pre-accept
        return self.value, self.childs

class Literal2(Literal):
    """
    This class overrides constructor because of
    the syntax difference of simplex and suplex routines.
    """
    def __init__(self, value):
        value = value[1:]
        super(Literal2, self).__init__(value)
