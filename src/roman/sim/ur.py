################################################################################################################################
## pybullet implementation of the URScript functions needed by the control layer. 
################################################################################################################################
import math
import pybullet as pb
import numpy as np
from scipy.spatial.transform import Rotation
from ..ur.scripts.constants import *

class URArm(object):
    # sim-specific constants
    SIM_MAX_JOINT_FORCE = 1000

    def __init__(self, body_id, base_joint_id, tcp_id, sim_time_step = 1/240.):
        self.body_id = body_id
        self.base_joint_id = base_joint_id
        self.ft_sensor_id = base_joint_id+7
        self.tcp_id = tcp_id
        self.joint_ids = range(base_joint_id, base_joint_id+6)
        self.sim_time_step = sim_time_step

    def reset(self):
        # start position is along the x axis, in negative direction 
        start_positions = [0, -math.pi/2, math.pi/2, -math.pi/2, -math.pi/2, 0]
        for i in range(6):
            pb.resetJointState(self.body_id, self.base_joint_id + i, start_positions[i])
        # dump joints:
        # for i in range(pb.getNumJoints(self.arm_id)):
        #     ji = pb.getJointInfo(self.arm_id, i)
        #     print(f"{i}: ix={ji[0]}, name={ji[1]}, link={ji[12]}")

    def get_inverse_kin(self, pose):
        '''Calculates the joint angles that corespond to the specified tool pose.'''
        joints = pb.calculateInverseKinematics(self.body_id, self.tcp_id, pose[0:3], Rotation.from_rotvec(pose[3:6]).as_quat())
        return joints[:6]

    def get_actual_tcp_pose(self):
        link_state = pb.getLinkState(self.body_id, self.tcp_id, computeLinkVelocity = 0, computeForwardKinematics = 1)
        pos = link_state[4]
        q = link_state[5]
        if q[3]>0:
            q = [*q[:3], -q[3]]
        rot = Rotation.from_quat(q).as_rotvec()
        return [pos[0], pos[1], pos[2], rot[0], rot[1], rot[2]]

    def get_actual_tcp_speed(self):
        link_state = pb.getLinkState(self.body_id, self.tcp_id, computeLinkVelocity = 1, computeForwardKinematics = 1)
        pos = link_state[6]
        rot = link_state[7]
        return [pos[0], pos[1], pos[2], rot[0], rot[1], rot[2]]

    def get_actual_joint_positions(self):
        joint_states = pb.getJointStates(self.body_id, self.joint_ids)
        joint_positions = [state[0] for state in joint_states]
        return joint_positions

    def get_actual_joint_speeds(self):
        joint_states = pb.getJointStates(self.body_id, self.joint_ids)
        joint_velocities = [state[1] for state in joint_states]
        return joint_velocities

    def get_target_tcp_pose(self):
        return [0,0,0,0,0,0]

    def get_target_tcp_speed(self):
        return [0,0,0,0,0,0]

    def get_target_joint_positions(self):
        return [0,0,0,0,0,0]

    def get_target_joint_speeds(self):
        return [0,0,0,0,0,0]

    def get_tcp_force(self):
        return [0,0,0,0,0,0]

    def ur_get_tcp_acceleration(self):
        return [0,0,0]

    def get_joint_torques(self):
        joint_states = pb.getJointStates(self.body_id, self.joint_ids)
        joint_torques = [state[3] for state in joint_states]
        return joint_torques


    def ur_get_tcp_sensor_force(self):
        tcp_state = pb.getJointState(self.body_id, self.tcp_id)
        return tcp_state[2]

    def speedj(self, speed, max_acc):
        current = self.get_actual_joint_speeds()
        for i in range(6):
            if current[i] < speed[i]:
                new_speed = min(speed[i], current[i] + max_acc*self.sim_time_step)    
            elif current[i] > speed[i]:
                new_speed = max(speed[i], current[i] - max_acc*self.sim_time_step)  
            else:
                new_speed = 0
            pb.setJointMotorControl2(self.body_id, 
                                    self.base_joint_id + i, 
                                    controlMode=pb.VELOCITY_CONTROL,
                                    targetVelocity = new_speed,
                                    force = URArm.SIM_MAX_JOINT_FORCE)

    def set_payload(self, m, cog):
        pass

    def set_tcp(self, pose):
        pass

