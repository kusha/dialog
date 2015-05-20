#!/usr/bin/env python3

from dialog import Dialog, handle
import execnet, time

movement_way = None
move_time = None
turn_way = None
look_way = None

def turn(responses):
    if turn_way == "left":
        z = 1 
    elif turn_way == "right":
        z = 1 
    else:
        responses.put("failure")
        return

    action_code = """
    import rospy, time
    from geometry_msgs.msg import Twist

    rospy.init_node('move')
    p = rospy.Publisher('/base_controller/command', Twist)
    turn = Twist()
    turn.linear.x = 0;
    turn.linear.y = 0; turn.linear.z = 0;       
    turn.angular.x = 0; turn.angular.y = 0;
    turn.angular.z = %i;
    times = 0
    while 1:
        times += 1
        p.publish(turn)
        rospy.sleep(%s)
        if times == %i:
            break
    twist = Twist()
    p.publish(twist)
    channel.send("success")
    """ % (z, "0.1", 40)
    gw = execnet.makegateway("popen//python=python2.7")
    channel = gw.remote_exec(action_code)
    if channel.receive() == "success":
        responses.put("success")

def picture(responses):
    action_code = """
    import rospy
    from sensor_msgs.msg import CompressedImage
    def callback(data):
        with open("image.jpg", "wb+") as f:
            f.write(data.data)
        
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("/narrow_stereo/left/image_mono/compressed", CompressedImage, callback)
    rospy.spin()

    channel.send("success")
    """
    gw = execnet.makegateway("popen//python=python2.7")
    channel = gw.remote_exec(action_code)
    if channel.receive() == "success":
        responses.put("success")


def look(responses):
    print(look_way)
    x, y = 0, 0
    if look_way == "left":
        y = 10
    elif look_way == "right":
        y = -10
    elif look_way == "top":
        x = 10
    elif look_way == "bottom":
        x = -10
    else:
        responses.put("failure")
        return

    action_code = """
    import roslib
    import rospy

    import actionlib
    from pr2_controllers_msgs.msg import PointHeadGoal, PointHeadAction
    from geometry_msgs.msg import PointStamped

    rospy.init_node('move_head_client_py')

    client = actionlib.SimpleActionClient("/head_traj_controller/point_head_action", PointHeadAction)
    client.wait_for_server()

    goal = PointHeadGoal()
    point = PointStamped()
    point.header.frame_id = "torso_lift_link"
    point.point.x = %i
    point.point.y = %i 
    point.point.z = 0
    goal.target = point;

    client.send_goal(goal)
    client.wait_for_result()
    client.get_result()

    channel.send("success")
    """ % (x, y)
    gw = execnet.makegateway("popen//python=python2.7")
    channel = gw.remote_exec(action_code)
    if channel.receive() == "success":
        responses.put("success")

# movement

def stop_movement(scope, responses):
    scope.stopped = True

def continue_movement(scope, responses):
    scope.stopped = False

callbacks = {
    "stop": stop_movement,
    "continue": continue_movement
}

def before(scope, responses):
    gw = execnet.makegateway("popen//python=python2.7")
    scope.channel = gw.remote_exec("""
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
    """ % (0.1, 0.1))
    scope.stopped = False
    if movement_way == "straight":
        scope.way = "forward"
    elif movement_way == "back":
        scope.way = "backward"
    else:
        responses.put("failed")
        scope._exit = True
    scope.move_time = int(scope.move_time)
    scope.distance = scope.move_time
    scope.position = 0

def after(scope, responses):
    scope.channel.send(None)
    if scope.channel.receive() == "success":
        pass

@handle(callbacks, before=before, after=after)
def movement(requests, responses, scope):
    if not scope.stopped:
        print(scope.position)
        scope.channel.send(scope.way)
        scope.position += 0.1
        time.sleep(0.1)
        if scope.position >= scope.distance:
            responses.put("finished")
            scope._exit = True

if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("control.dlg")
    DLG.start()