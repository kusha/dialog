#!/usr/bin/env python3

"""
ROB 2015

Robot movement interface.
"""
import random, sys

from dialog import Dialog, handle

# import execnet
# gw = execnet.makegateway("popen//python=python2.7")
# channel = gw.remote_exec("""
#     import rospy
#     from geometry_msgs.msg import Twist
#     rospy.init_node('move')
#     p = rospy.Publisher('/base_controller/command', Twist)
#     while True:
#         # command format
#         # lx ly lz ax ay az d
#         command = channel.receive()
#         values = [float(i) for i in command.split(' ')]
#         channel.send("accepted")
#         movement = Twist()
#         movement.linear.x = values[0]
#         movement.linear.y = values[1]
#         movement.linear.z = values[2]
#         movement.angular.x = values[3]
#         movement.angular.y = values[4]
#         movement.angular.z = values[5]
#         p.publish(movement)
#         rospy.sleep(values[6])
# """)


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
    if len(sys.argv) > 1:
        option = sys.argv[1]
        if option == "-t":
            DLG.start()
        elif option == "-s":
            DLG.start_spoken()
        elif option == "-o":
            DLG.start_offline()

