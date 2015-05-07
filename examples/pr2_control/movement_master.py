 #!/usr/bin/env python3

"""
Dialog system controls PR2 movement.

"""

from dialog import Dialog, handle

import time
import execnet

speed = 0.1
delay = 0.1

gw = execnet.makegateway("popen//python=python2.7")
channel = gw.remote_exec("""
    import rospy
    from geometry_msgs.msg import Twist
    x_speed = %s
    rospy.init_node('move')
    p = rospy.Publisher('/base_controller/command', Twist)
    forward = Twist()
    forward.linear.x = x_speed;
    forward.linear.y = 0; forward.linear.z = 0;       
    forward.angular.x = 0; forward.angular.y = 0;
    forward.angular.z = 0;
    backward = Twist()
    backward.linear.x = -x_speed;
    backward.linear.y = 0; backward.linear.z = 0;       
    backward.angular.x = 0; backward.angular.y = 0;
    backward.angular.z = 0;
    # rospy.loginfo("About to be moving forward!")
    while 1:
        x = channel.receive()
        if x is None:
            break
        elif x == "forward":
            p.publish(forward)
        elif x == "backward":
            p.publish(backward)
        rospy.sleep(%s)
    # rospy.loginfo("Stopping!")
    twist = Twist()
    p.publish(twist)
    channel.send("success")
""" % (speed, delay))

# for x in range(30):
#     channel.send(x)
# channel.send(None)
# print (channel.receive())

def stop_movement(scope):
    scope.stopped = True

def continue_movement(scope):
    scope.stopped = False

def revert_movement(scope):
    if scope.way == "forward":
        scope.way = "backward"
        scope.speed = 0 - scope.speed
    elif scope.way == "backward":
        scope.way = "forward"
        scope.speed = 0 - scope.speed

callbacks = {
    "stop": stop_movement,
    "continue": continue_movement,
    "way": revert_movement,
}

def before(scope):
    scope.stopped = False
    scope.way = "forward"
    scope.distance = int(scope.distance)*10
    scope.position = 0
    scope.half_was = False

def after(scope):
    channel.send(None)
    if channel.receive() == "success":
        pass

@handle(callbacks, before=before)
def movement(requests, responses, scope):
    if not scope.stopped:
        print(scope.position)
        channel.send(scope.way)
        scope.position += scope.speed
        scope.half_new = scope.position >= scope.distance/2
        time.sleep(scope.delay)
        if scope.position <= 0:
            responses.put("reverted")
            scope._exit = True
        elif scope.position >= scope.distance:
            responses.put("finished")
            scope._exit = True
        elif scope.half_new != scope.half_was:
            responses.put("half")
        scope.half_was = scope.half_new

if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("examples/movement.dlg")
    DLG.start_text()
