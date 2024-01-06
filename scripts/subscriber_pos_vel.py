#! /usr/bin/env python3

import sys
import rospy
import time
import math
from geometry_msgs.msg import Point, Pose, Twist
from nav_msgs.msg import Odometry
import actionlib
import actionlib.msg
import second_assignment.msg
from second_assignment.msg import Pos_vel
from second_assignment.msg import PlanningAction, PlanningGoal, PlanningResult
from second_assignment.srv import Dist_vel, Dist_velResponse
from std_srvs.srv import SetBool
from actionlib_msgs.msg import GoalStatus

global distance, average_speed
distance = 0.0
average_speed = 0.0

def callback_function(pos_vel):
    global distance, average_speed

    velocities = []
    window_size = rospy.get_param('window_size')

    goal_x = rospy.get_param('des_pos_x')
    goal_y = rospy.get_param('des_pos_y')

    actual_x = pos_vel.x
    actual_y = pos_vel.y

    distance = math.sqrt((goal_x - actual_x)**2 + (goal_y - actual_y)**2)
    # rospy.loginfo(f"distance: {distance}")

    velocities.append(pos_vel.vel_x)
    if len(velocities) > window_size:
        velocities = velocities[-window_size:]
    
    total_speed = sum(velocities)
    average_speed = total_speed / len(velocities)
    # rospy.loginfo(f"average_speed: {average_speed}")

def service_callback(_):
    global distance, average_speed

    # rospy.loginfo(f"distance: {distance} average_speed: {average_speed}")
    return Dist_velResponse(distance, average_speed)


if __name__ == '__main__':
    try:
        rospy.init_node('subscriber_pos_vel')
        rospy.loginfo("subscriber_pos_vel node initialized")

        rospy.Subscriber("pos_vel_topic", Pos_vel, callback_function)

        s = rospy.Service('dist_vel_service', Dist_vel, service_callback)

        rospy.loginfo("service ready")

        # Wait for the service to become available
        rospy.wait_for_service('dist_vel_service')

        # Create a proxy for the service
        dist_vel_service = rospy.ServiceProxy('dist_vel_service', Dist_vel)

        # Create a Rate object to control the loop rate
        rate = rospy.Rate(1)  # 1 Hz

        # Loop until the node is shut down
        while not rospy.is_shutdown():
            # Call the service
            response = dist_vel_service()

            rospy.loginfo(f"Service response: {response}")

            # Sleep for the rest of the loop period
            rate.sleep()

    except rospy.ROSInterruptException:
        print("program interrupted before completion", file=sys.stderr)