#!/usr/bin/env python3

"""
Link parser Python bindings.
"""
__author__ = "Mark Birger"
__date__ = "19 Jan 2015"

import subprocess, re, shelve, sys
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
        ['link-grammar-5.2.5/link-parser/link-parser', '-postscript', '-graphics', '-verbosity=0'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout_data = proc.communicate(input=string.encode('utf-8'))[0]
    stdout = stdout_data.decode('utf-8')
    if proc.returncode != 0:
        print("ERROR: dialog system is unable to run link-parser")
        sys.exit(1)
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
        link[2] = generalize_link(link[2])
        result["links"].append(link)
    cache[string] = result
    return result

def generalize_link(link_type):
    return re.findall(r"^[A-Z]*", link_type)[0]

def compare(flexibles, sentence_self, sentence_input):
    # print(sentence_self)
    # print(sentence_input)
    # print(flexibles)
    subs_self = substitute(sentence_self, flexibles)
    subs_input = substitute(sentence_input)
    # print(subs_self)
    # print(subs_input)
    equal_links = 0
    for link1 in subs_self:
        for link2 in subs_input:
                # if link1[0] in link2[0] and \
                    # link1[1] in link2[1] and \
                # print(subs_self, subs_input)
                # print(link1[0], link2[0])
                # print(link1[1], link2[1])
                # print(link1[2], link2[2])
                if (link1[0][0] in link2[0][0]) == link1[0][1]  and \
                    (link1[1][0] in link2[1][0]) == link1[1][1] and \
                    link1[2] == link2[2]:
                    # print("OK")
                    # print(link1, "\t", link2)
                    equal_links += 1
    # TODO: understand why it is problem here
    if len(subs_self) != 0:
        # print(similarity, len(subs_self), len(subs_input))
        similarity = equal_links/len(subs_self)
    else:
        similarity = 0
    return similarity, equal_links

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
        # copy[2] = generalize_link(copy[2])
        important.append(copy)
    return important    

def extract(idx, sentence1, sentence2):
    """
    Extracts word from sentence with similar structure.
    """
    # print(idx, sentence1, sentence2)
    important = word_links(idx, sentence1)
    # print(important)
    for word in range(len(sentence2["words"])):
        links = word_links(word, sentence2)
        # print(word, links)
        needed = important[:]
        for link in links:
            if link in needed:
                needed.remove(link)
        if len(needed) == 0:
            #TODO: check is it can be more results?
            result = re.findall(r"\w+", sentence2["words"][word])[0]
            return result

def substitute(sentence, clean=[]):
    words_wo_flex = [[word, True] for word in sentence["words"]]
    for idx in clean:
        pos_tag = re.findall(r"\..*$", words_wo_flex[idx][0])
        if len(pos_tag):
            words_wo_flex[idx][0] = pos_tag[0]
        else:
            words_wo_flex[idx][0] = "."
            words_wo_flex[idx][1] = False
    result = []
    for link in sentence["links"]:
        first = words_wo_flex[link[0]]
        second = words_wo_flex[link[1]]
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
