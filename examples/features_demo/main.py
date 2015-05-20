#!/usr/bin/env python3

"""
Evaluation tests.

"""

from dialog import Dialog, handle
import datetime, time


# Substitution
def get_time():
    now = datetime.datetime.now()
    return str(now.hour) + ' ' + str(now.minute)

name = "PR2"

# Fixed setters
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

# Flexible setters
collocutor = None

# Simplex routines
def make_coffee(responses):
    print("routine started")
    time.sleep(5)
    responses.put('no sugar')

def make_wo_sugar(responses):
    time.sleep(4)
    responses.put(True)


# Duplex routines
value = 0

def stop_count(scope, responses):
    scope.stop_flag = True

def continue_count(scope, responses):
    scope.stop_flag = False

def countdown(scope, responses):
    scope.stop_flag = False
    scope.step = -1 * scope.step
    # print("*move back*")

callbacks = {
    "stop": stop_count,
    "continue": continue_count,
    "back": countdown,
}

def before(scope, responses):
    scope.stop_flag = False
    # scope.pos = 0
    scope.step = 7

def after(scope, responses):
    pass
     
@handle(callbacks, before=before, after=after)
def count(requests, responses, scope):
    if not scope.stop_flag:
        time.sleep(2)
        scope.value += scope.step
        print("Rtn>\t", scope.value)
        if scope.value == 21:
            print('HALF')
            responses.put("half")
        elif scope.value == 42:
            responses.put("finished")
            scope._exit = True
        elif scope.value == 0:
            responses.put("reverted")
            scope._exit = True
        # print("*my pos is %s*" % scope.pos)
    else:
        time.sleep(2)
        # print("*do nothing*")

# Running a dialog system
if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("examples/features_demo/demo.dlg")
    DLG.start()
