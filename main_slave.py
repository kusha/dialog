#!/usr/bin/env python3

"""
Example of dialog manager usage.

"""

from dialog import handle # needed for duplex routine

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

# simplex routine

def make_coffee(responses):
    print("routine started")
    time.sleep(5)
    responses.put('no sugar')

def make_wo_sugar(responses):
    time.sleep(4)
    responses.put(True)

# duplex routine

def stop_count(scope):
    scope.stop_flag = True

def continue_count(scope):
    scope.stop_flag = False

def revert_count(scope):
    scope.stop_flag = False
    scope.step = -7

callbacks = {
    "stop": stop_count,
    "continue": continue_count,
    "back": revert_count,
}

def before(scope):
    scope.stop_flag = False
    scope.pos = 0
    scope.step = 7

def after(scope):
    responses.put("finished")

@handle(callbacks, before=before, after=after)
def count(requests, responses, scope):
    if not scope.stop_flag:
        time.sleep(2)
        scope.pos += scope.step
        if scope.pos == 21 and scope.step > 0:
            responses.put("half")
        elif scope.pos == 42:
            responses.put("counted")
            scope._exit = True
        elif scope.pos == 0:
            responses.put("reverted")
            scope._exit = True
    else:
        time.sleep(2)

export = globals()
