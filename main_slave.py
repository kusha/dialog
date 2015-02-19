#!/usr/bin/env python3

"""
Example of dialog manager usage.

"""

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

export = globals()