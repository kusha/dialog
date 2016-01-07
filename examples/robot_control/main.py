#!/usr/bin/env python3

"""
ROB 2015

Robot movement interface.
"""
import random


from dialog import Dialog, handle

target = None


def move_target(responses):
	ways = ['forward', 'backward', 'left', 'right']
	if target == "somewhere":
		target = random.choice(ways)
		responses.put('somewhere')
	else:
		print("ok")
		responses.put('unknown')
    # print("routine started")
    # time.sleep(5)
    # responses.put('no sugar')



speed = 3.0
speed_text = "normally"

def update_speed():
	message = ""
	if speed_text == "fast":
		speed = 5.0
	elif speed_text == "slowly":
		speed = 3.0
	elif speed_text == "normally":
		speed = 1.0
	else:
		return "i don't know how to move "+speed_text
	if not moving:
		message += "as for now i'm staying. "
		message += "i will move %s next time. " % (speed_text)
	else:
		message += "okay, moving %s. " % (speed_text)
	return message


moving = False

if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("examples/robot_control/dialog.dlg")
    DLG.start()