#!/usr/bin/env python3

"""
Example of dialog manager usage.

"""


from dialog import Dialog, handle

import datetime, time

def greetings():
    return "Hello " + collocutor

name = "PR2"

def get_time():
    now = datetime.datetime.now()
    return str(now.hour) + ' ' + str(now.minute)

def is_angry():
    try:
        if angry == True: 
            return "You are angry"
        else:
            return "You aren't angry"
    except NameError:
        return "i don't know"

def day_of_week():
    days = ['Mon','Tues','Wednes','Thurs','Fri','Satur','Sun']
    return days[datetime.datetime.now().weekday()] + 'day'

def make_coffee(responses):
    print("routine started")
    time.sleep(5)
    responses.put('no sugar')

def make_wo_sugar(responses):
    time.sleep(4)
    responses.put(True)

# two-way activity
i = 10

def fucnt():
    i = 11
    return i

# functions definition
def stop_movement(scope):
    scope.stop_flag = True
    print("*stop movement*")

def continue_movement(scope):
    scope.stop_flag = False
    print("*continuing movement*")

def revert_movement(scope):
    scope.stop_flag = False
    scope.step = -1
    print("*move back*")

callbacks = {
    "stop": stop_movement,
    "continue": continue_movement,
    "back": revert_movement,
}

def before(scope):
    scope.stop_flag = False
    scope.pos = 0
    scope.step = 1
    print("*calculating trajectory*")

def after(scope):
    print("*disabling motors*")

@handle(callbacks, before=before, after=after)
def movement(requests, responses, scope):
    if not scope.stop_flag:
        time.sleep(2)
        scope.pos += scope.step
        if scope.pos == 5:
            responses.put("half")
        elif scope.pos == 10:
            responses.put("finished")
            scope._exit = True
        elif scope.pos == 0:
            responses.put("reverted")
            scope._exit = True
        print("*my pos is %s*", scope.pos)
    else:
        time.sleep(2)
        print("*do nothing*")

# news reader
import feedparser, re, random, html.parser
html_parser = html.parser.HTMLParser()
news = {}
feedparser._HTMLSanitizer.acceptable_elements = set()
def update_news(responses):
    if not news:
        responses.put('checkout')
        result = feedparser.parse("http://techcrunch.com/feed/")
        for entry in result['entries']:
            entry['summary'] = re.sub('<img[^>]*>', '', entry['summary'])
            entry['summary'] = re.sub('<a.*</a>', '', entry['summary'])
            entry['summary'] = html_parser.unescape(entry['summary'])
            news[entry['title']] = entry['summary']
        responses.put('updated')
    else:
        responses.put('ready')

current = None
def read_news():
    try:
        selected = random.choice(list(news.keys()))
    except IndexError:
        return "I'm not ready to read news yet" #random choice fix
    current = news[selected]
    return selected

if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("examples/tickets.dlg")
    DLG.start_spoken()
