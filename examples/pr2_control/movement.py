#!/usr/bin/env python3

# connect to robodev1
# ssh -L 5905:localhost:5905 xbirge00@robodev1.fit.vutbr.cz
# /opt/TurboVNC/bin/vncviewer -user xbirge00 localhost:5905

# install gazebo worlds
# source /opt/ros/hydro/setup.bash
# mkdir -p ~/Desktop/catkib_gazebo/src
# cd ~/Desktop/catkib_gazebo/src
# catkin_init_workspace
# svn co https://code.ros.org/svn/ros-pkg/stacks/simulator_gazebo/branches/hydro/ simulator_gazebo
# svn co https://code.ros.org/svn/wg-ros-pkg/stacks/pr2_simulator/trunk pr2_simulator
# cd ~/Desktop/catkib_gazebo/
# catkin_make
# source devel/setup.bash

# run simulation
# roslaunch gazebo_worlds empty_world.launch
# roslaunch pr2_gazebo pr2.launch
# roslaunch pr2_teleop teleop_keyboard.launch

# prepare python
# sudo apt-get install python3-setuptools
# sudo easy_install3 pip
# sudo pip3 install catkin_pkg

# We always import roslib, and load the manifest to handle dependencies
import roslib; #roslib.load_manifest('mini_max_tutorials')
import rospy

# recall: robots generally take base movement commands on a topic 
#  called "cmd_vel" using a message type "geometry_msgs/Twist"
from geometry_msgs.msg import Twist

x_speed = 0.1  # 0.1 m/s

if __name__=="__main__":

    # first thing, init a node!
    rospy.init_node('move')

    # publish to cmd_vel
    p = rospy.Publisher('cmd_vel', Twist)

    # create a twist message, fill in the details
    twist = Twist()
    twist.linear.x = x_speed;                   # our forward speed
    twist.linear.y = 0; twist.linear.z = 0;     # we can't use these!        
    twist.angular.x = 0; twist.angular.y = 0;   #          or these!
    twist.angular.z = 0;                        # no rotation

    # announce move, and publish the message
    rospy.loginfo("About to be moving forward!")
    for i in range(30):
        p.publish(twist)
        rospy.sleep(0.1) # 30*0.1 = 3.0

    # create a new message
    twist = Twist()

    # note: everything defaults to 0 in twist, if we don't fill it in, we stop!
    rospy.loginfo("Stopping!")
    p.publish(twist)