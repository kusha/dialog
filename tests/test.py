#!/usr/bin/env python3

# pylint: disable=line-too-long, R0904, W0212
# Lines are long becuase it's about text processing
# Too many public methods in unittest by default
# We are testing private methods too

"""
Tests for phrase module.
"""
__author__ = "Mark Birger"
__date__ = "30 Mar 2015"

import unittest
from phrase import Phrase
from scope import Scope
import link_parser

class SimpleMethods(unittest.TestCase):
    """
    Tests for simplest one-block methods.
    """

    def setUp(self):
        self.phrase = Phrase("Hello world", Scope())

    def test_create_substition(self):
        self.phrase.substitute.append(["my_var", 1, 5])
        self.assertEqual(self.phrase.substitute, [["my_var", 1, 5]])

    def test_create_fixed_setter(self):
        self.phrase.setters.append(["my_var", "34", 6, 9])
        self.assertEqual(self.phrase.setters, [["my_var", "34", 6, 9]])

    def test_create_flexible_setter(self):
        self.phrase.flexibles.append(["name", "John", 10, 15, None])
        self.assertEqual(self.phrase.flexibles, [["name", "John", 10, 15, None]])

    def test_create_routine_request(self):
        self.phrase.requests.append(["routine1", "stop", 17, 20])
        self.assertEqual(self.phrase.requests, [["routine1", "stop", 17, 20]])

class ParsingTestShifters(unittest.TestCase):
    """
    Tests for setters manipulations.
    """

    def setUp(self):
        self.phrase = Phrase("Another string for testing", Scope())

    @unittest.skip("Pronouncable validation isn't yet implemented.")
    def test_validate(self):
        pass

    def test_shift_other(self):
        # Edge Coverage implemented

        # this setters won't be shifted (before)
        self.phrase._create_substition("my_var", 1, 7)
        self.phrase._create_fixed_setter("my_var", "34", 9, 15)
        self.phrase._create_flexible_setter("name", "John", 19, 25)
        self.phrase._create_routine_request("routine1", "stop", 26, 30)

        # shifter is not substitution!
        # substitution is evaluated inside the eval method

        shifter = ["my_var", "34", 32, 35]
        length = 3 # shift all afters by 3

        # this setters should be shifted (after)
        self.phrase._create_substition("my_var", 36, 39)
        self.phrase._create_fixed_setter("my_var", "34", 40, 45)
        self.phrase._create_flexible_setter("name", "John", 52, 56)
        self.phrase._create_routine_request("routine1", "stop", 60, 63)

        self.phrase._shift_other(shifter, length)

        self.assertEqual(self.phrase.substitute[0], ["my_var", 1, 7])
        self.assertEqual(self.phrase.substitute[1], ["my_var", 33, 36])

        self.assertEqual(self.phrase.setters[0], ["my_var", "34", 9, 15])
        self.assertEqual(self.phrase.setters[1], ["my_var", "34", 37, 42])

        self.assertEqual(self.phrase.flexibles[0], ["name", "John", 19, 25, None])
        self.assertEqual(self.phrase.flexibles[1], ["name", "John", 49, 53, None])

        self.assertEqual(self.phrase.requests[0], ["routine1", "stop", 26, 30])
        self.assertEqual(self.phrase.requests[1], ["routine1", "stop", 57, 60])

class ParsingTestErasers(unittest.TestCase):
    """
    Tests for phrase parsing. (already parses string)
    Edge Pair Coverage implemented.
    """

    def setUp(self):

        class IncompeleteInitializedPhrase(Phrase):
            _erase_fixed_setters = None
            _erase_flexible_setters = None
            _erase_routine_requests = None
            def __init__(self, origin, scope):
                try:
                    # pylint has a problems with locally defined class
                    # pylint: disable=E1003
                    super(IncompeleteInitializedPhrase, self).__init__(origin, scope)
                except TypeError:
                    pass

        self.fake_class = IncompeleteInitializedPhrase

    def test_erase_fixed_setters(self):

        # origin = 'Hello world `my_var:32` `name~John` `routine1<"stop"`'

        phrase = self.fake_class('Hello world `name~John` `routine1<"stop"`', Scope())
        Phrase._erase_fixed_setters(phrase)
        self.assertEqual(phrase.phrase, 'Hello world `name~John` `routine1<"stop"`')

        phrase = self.fake_class('Hello world `my_var:32` `name~John` `my_var:32` `routine1<"stop"`', Scope())
        Phrase._erase_fixed_setters(phrase)
        self.assertEqual(phrase.phrase, 'Hello world  `name~John`  `routine1<"stop"`')
        # two whitespaces is predicted behavior!

    def test_erase_flexible_setters(self):

        phrase = self.fake_class('Hello world `my_var:32` `routine1<"stop"`', Scope())
        Phrase._erase_flexible_setters(phrase)
        self.assertEqual(phrase.phrase, 'Hello world `my_var:32` `routine1<"stop"`')

        phrase = self.fake_class('Hello world `name~John` `my_var:32` `name~Mike` `routine1<"stop"`', Scope())
        Phrase._erase_flexible_setters(phrase)
        self.assertEqual(phrase.phrase, 'Hello world John `my_var:32` Mike `routine1<"stop"`')

    def test_erase_routine_requests(self):

        phrase = self.fake_class('Hello world `my_var:32` `name~John`', Scope())
        Phrase._erase_routine_requests(phrase)
        self.assertEqual(phrase.phrase, 'Hello world `my_var:32` `name~John`')

        phrase = self.fake_class('Hello world `routine1<"stop"` `my_var:32` `routine1<"stop"` `name~John`', Scope())
        Phrase._erase_routine_requests(phrase)
        self.assertEqual(phrase.phrase, 'Hello world  `my_var:32`  `name~John`')

class ParsingTest(unittest.TestCase):
    """
    Tests for main parse function. 
    """

    def test_parse_regex(self):

        # Is indentifier should be Pythonic?

        expressions = []

        def r_star(string):
            r_question(string+"")
            r_question(string+"a")
            r_question(string+"azAz09_")

        def r_question(string):
            r_end(string+"")
            r_type(string)
            r_double_type(string)

        def r_type(string):
            r_value(string+":")
            r_value(string+"~")
            r_value(string+"<")

        def r_value(string):
            r_end(string+"")
            r_end(string+"`")
            r_end(string+"a")
            r_end(string+"aaa")
            r_end(string+"a`a")

        def r_double_type(string):
            r_double_value(string+":")
            r_double_value(string+"~")
            r_double_value(string+"<")

        def r_double_value(string):
            r_type(string+"")
            r_type(string+"`")
            r_type(string+"a")
            r_type(string+"aaa")
            r_type(string+"a`a")

        def r_end(string):
            nonlocal expressions
            expressions.append(string+"`")

        r_star("`")

        # print(len(expressions), "generated")

        count_not_parsed = 0

        for expression in expressions:
            phrase = Phrase(expression, Scope())
            summary = len(phrase.substitute) + \
                len(phrase.setters) + \
                len(phrase.flexibles) + \
                len(phrase.requests)
            if summary == 0:
                count_not_parsed += 1
            self.assertFalse(expression.count('`') == 3 and summary > 1)
            self.assertFalse(summary == 2 and len(phrase.substitute) == 0)
            self.assertFalse(summary == 3)

        # print(count_not_parsed, "not parsed")

    def test_parse(self):

        phrase = 'Hello `my_var` `my_var:32` `name~John` `routine1<"stop"`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.latest, 'Hello value  John ')
        self.assertEqual(phrase.phrase, 'Hello `my_var`  John ')
        self.assertEqual(phrase.substitute, [['my_var', 6, 14]])
        self.assertEqual(len(phrase.setters), 1)
        self.assertEqual(phrase.flexibles, [['name', 'John', 16, 20, None]])
        self.assertEqual(len(phrase.requests), 1)

        # exception raised by Scope module
        phrase = 'Hello `undefined_var`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.latest, None)

class UsageTest(unittest.TestCase):
    """
    Tests for usage of parsed structures. 
    """

    def test_init(self):

        phrase_text = 'Hello `my_var` `my_var:32` `name~John` `routine1<"stop"`'
        phrase = Phrase(phrase_text, Scope())
        self.assertIsInstance(phrase.scope, Scope)
        self.assertEqual(phrase.origin, phrase_text)
        self.assertEqual(phrase.phrase, "Hello `my_var`  John ")
        self.assertEqual(phrase.substitute, [['my_var', 6, 14]])
        self.assertEqual(phrase.setters, [['my_var', '32', 15, 26]])
        self.assertEqual(phrase.flexibles, [['name', 'John', 16, 20, None]])
        self.assertEqual(phrase.requests, [['routine1', '"stop"', 21, 38]])
        self.assertEqual(phrase.latest, "Hello value  John ")
        self.assertEqual(phrase.parsed, {'links': [], 'words': []})

    def test_link_flexible_setters(self):

        # we can test linking at the initalization

        phrase = 'my name is not setted'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.flexibles, [])

        phrase = 'my name is `name~Mark` and i do like `objects~cats`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.flexibles, \
            [['name', 'Mark', 11, 15, 4], ['objects', 'cats', 30, 34, 9]])
        # flexible setter is linked with #4 and #9 in sentence
        # my name is Mark and i do like cats

        # known bug
        phrase = '`object1~word` is `object2~word`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.flexibles, \
            [['object1', 'word', 0, 4, 1], ['object2', 'word', 8, 12, 3]])

    def test_evaluate(self):

        phrase = 'no substitutions'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.evaluate(), "no substitutions")

        phrase = 'iteratable value is `iteratable`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.evaluate(), "iteratable value is 2") # 1 is passed by init call
        self.assertEqual(phrase.evaluate(), "iteratable value is 3")
        self.assertEqual(phrase.evaluate(), "iteratable value is 4")

        phrase = 'undefined value is `undefined_var`'
        phrase = Phrase(phrase, Scope())
        self.assertRaises(KeyError, phrase.evaluate) # predicted behavior

    def test_update_parsed(self):

        scope = Scope()

        phrase = 'changeable value is `changeable`'
        phrase = Phrase(phrase, scope)
        phrase._update_parsed()
        self.assertEqual(phrase.latest, "changeable value is True")
        # no exception

        scope.change()
        phrase._update_parsed()
        self.assertEqual(phrase.latest, "changeable value is False")
        # no exception

        scope.change()
        scope.raise_error()
        self.assertRaises(KeyError, phrase._update_parsed)
    
        # also test not changed, with exception 
        scope = Scope()
        phrase = 'changeable value is `changeable`'
        phrase = Phrase(phrase, scope)
        phrase._update_parsed()
        self.assertEqual(phrase.latest, "changeable value is True")
        scope.raise_error()
        self.assertRaises(KeyError, phrase._update_parsed)
        #TODO: delegate raises to accept and compare methods

    def test_str(self):

        phrase = 'Hello world `substitution` `my_var:32` `name~John` `routine1<"stop"`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(str(phrase), phrase.evaluate())

    def test_compare(self):

        input_string = "my name is John"
        input_parsed = link_parser.parse(input_string)

        phrase = 'my name is `name~Mark`'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.compare(input_parsed), 0.8) #4/5 simlar links

        phrase = 'hello'
        phrase = Phrase(phrase, Scope())
        self.assertEqual(phrase.compare(input_parsed), 0)
        # no links in hello sentence, beacuase it is not in fake module

    def test_accept(self):

        scope = Scope()
        phrase = '`var:13` my name is `name~Jack` `surname~Daniels` `strvar:"string"` `routine<1` `routine2<"ok"`'
        phrase = Phrase(phrase, scope)
        phrase.accept('my name is John Walker')
        self.assertEqual(scope.toset, {'var': 13, 'name': 'example', 'surname': 'example', 'strvar': 'string'})
        self.assertEqual(scope.tosend, {'routine': 1, 'routine2': 'ok'})

        scope = Scope()
        phrase = Phrase("Hello world", scope)
        phrase.accept()
        self.assertEqual(scope.toset, {})
        self.assertEqual(scope.tosend, {})


if __name__ == '__main__':
    unittest.main()
