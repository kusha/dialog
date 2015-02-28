#!/usr/bin/env python3

"""
Example of dialog manager usage.

"""


from dialog import Dialog

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
    DLG.start_text()
