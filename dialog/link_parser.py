#!/usr/bin/env python3

"""
Link parser Python bindings.
"""
__author__ = "Mark Birger"
__date__ = "19 Jan 2015"

import subprocess, re, shelve
from dialog import STORAGEPATH

def parse(string):
    """
    Link-parser output data parser.
    """
    global STORAGEPATH
    cache = shelve.open(STORAGEPATH + "/sentences")
    if string in cache:
        return cache[string]
    proc = subprocess.Popen(
        ['link-parser', '-postscript', '-graphics', '-verbosity=0'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout_data = proc.communicate(input=string.encode('utf-8'))[0]
    stdout = stdout_data.decode('utf-8')
    # filter newlines
    r_unwanted = re.compile("[\n\t\r]")
    stdout = r_unwanted.sub("", stdout)
    # find needed information
    parsed = re.findall(r"\[(.*?)\]\[(.*)\]\[.*?\]", stdout)[0]
    result = {}
    # creating structure
    result["words"] = re.findall(r"\((.*?)\)", parsed[0])
    result["links"] = []
    links = re.findall(r"(\[(\d+) (\d+) (\d+) \((.*?)\)\])", parsed[1])
    for link in links:
        link = list(link) # was returned tuple
        del link[3] # ignoring height level of the link
        del link[0]
        link[0] = int(link[0])
        link[1] = int(link[1])
        result["links"].append(link)
    cache[string] = result
    return result

def word_links(idx, sentence):
    important = []
    for link in sentence["links"]:
        copy = link[:]
        if link[0] == idx:
            copy[0] = None
            copy[1] = sentence["words"][link[1]]
        elif link[1] == idx:
            copy[0] = sentence["words"][link[0]]
            copy[1] = None
        else:
            continue
        important.append(copy)
    return important    

def extract(idx, sentence1, sentence2):
    """
    Extracts word from sentence with similar structure.
    """
    important = word_links(idx, sentence1)
    for word in range(len(sentence2["words"])):
        links = word_links(word, sentence2)
        needed = important[:]
        for link in links:
            if link in needed:
                needed.remove(link)
        if len(needed) == 0:
            #TODO: check is it can be more results?
            result = re.findall(r"\w+", sentence2["words"][word])[0]
            return result

def substitute(sentence):
    result = []
    for link in sentence["links"]:
        first = sentence["words"][link[0]]
        second = sentence["words"][link[1]]
        result.append([first, second, link[2]])
    return result

# s1 = parse("What is your mark, Mark")
# print(s1["words"])
# print(s1["links"])
# s2 = parse("What is your mark, John")
# print(s2["words"])
# print(s2["links"])
# print()
# word = substruct(6, s1, s2)
# print(word)
