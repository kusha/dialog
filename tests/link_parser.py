#!/usr/bin/env python3

"""
Fake module for testing.
Imitiates link-parser bindings.
"""
__author__ = "Mark Birger"
__date__ = "4 Apr 2015"

def parse(string):
    if string == "Hello world":
        return {'links': [[0, 2, 'Wa'], [1, 2, 'AN']], 'words': ['LEFT-WALL', 'hello.n', 'world.n']}
    elif string == "Another string for testing":
        return {'links': [[0, 4, 'Wa'], [2, 4, 'AN']], 'words': ['LEFT-WALL', '[Another]', 'string.s', '[for]', 'testing.n-u']}
    elif string == "word is word":
        return {'links': [[0, 3, 'Wa'], [1, 3, 'AN']], 'words': ['LEFT-WALL', 'word.n', '[is]', 'word.n']}
    elif string == "my name is Mark and i do like cats":
        return {'links': [[0, 5, 'WV'], [0, 2, 'Wd'], [2, 5, 'Ss'], [1, 2, 'Ds**c'], [3, 5, 'VJlsi'], [3, 4, 'Osm'], [5, 8, 'MVp'], [5, 7, 'VJrsi'], [8, 9, 'Jp']], 'words': ['LEFT-WALL', 'my.p', 'name.n', 'is.v', 'Mark.b', 'and.j-v', '[i]', 'do.v', 'like.p', 'cats.n']}
    elif string == "my name is Mark":
        return {'links': [[0, 3, 'WV'], [0, 2, 'Wd'], [2, 3, 'Ss'], [1, 2, 'Ds**c'], [3, 4, 'Ost']], 'words': ['LEFT-WALL', 'my.p', 'name.n', 'is.v', 'Mark.b']}
    elif string == "my name is John":
        return {'words': ['LEFT-WALL', 'my.p', 'name.n', 'is.v', 'John.m'], 'links': [[0, 3, 'WV'], [0, 2, 'Wd'], [2, 3, 'Ss'], [1, 2, 'Ds**c'], [3, 4, 'Ost']]}
    else:
        return {'links': [], 'words': []}

def substitute(sentence):
    """
    Real method. Too simple to be fake.
    """
    result = []
    for link in sentence["links"]:
        first = sentence["words"][link[0]]
        second = sentence["words"][link[1]]
        result.append([first, second, link[2]])
    return result

def extract(idx, sentence1, sentence2):
    return "example"