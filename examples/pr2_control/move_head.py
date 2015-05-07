#! /usr/bin/env python

import roslib#; roslib.load_manifest('actionlib_tutorials')
import rospy

import actionlib
from pr2_controllers_msgs.msg import PointHeadGoal, PointHeadAction
from geometry_msgs.msg import PointStamped

def move_head_client():
    client = actionlib.SimpleActionClient("/head_traj_controller/point_head_action", PointHeadAction)

    # Waits until the action server has started up and started
    # listening for goals.
    client.wait_for_server()

    # Creates a goal to send to the action server.
    goal = PointHeadGoal()

    point = PointStamped()
    point.header.frame_id = "torso_lift_link"
    point.point.x = 0
    point.point.y = 0 
    point.point.z = 0
    goal.target = point;

    # Sends the goal to the action server.
    client.send_goal(goal)

    # Waits for the server to finish performing the action.
    client.wait_for_result()

    # Prints out the result of executing the action
    return client.get_result()  # A FibonacciResult

if __name__ == '__main__':
    try:
        # Initializes a rospy node so that the SimpleActionClient can
        # publish and subscribe over ROS.
        rospy.init_node('move_head_client_py')
        result = move_head_client()
        # print "Result:", ', '.join([str(n) for n in result.sequence])
    except rospy.ROSInterruptException:
        print ("program interrupted before completion")