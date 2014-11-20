#!/usr/bin/env python3

"""
Example of dialog manager usage.

"""

from dialog import Dialog

import datetime

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


if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("examples/tickets.dlg")
    DLG.start()
