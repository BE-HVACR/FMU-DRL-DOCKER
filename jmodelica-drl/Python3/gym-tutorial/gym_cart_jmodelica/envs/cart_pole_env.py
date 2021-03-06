# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

"""
Classic cart-pole example implemented with an FMU simulating a cart-pole system.
Implementation inspired by OpenAI Gym examples:
https://github.com/openai/gym/blob/master/gym/envs/classic_control/cartpole.py
"""

import logging
import math
import numpy as np
from gym import spaces
from modelicagym.environment import FMI2CSEnv, FMI1CSEnv
import os

logger = logging.getLogger(__name__)


NINETY_DEGREES_IN_RAD = (90 / 180) * math.pi
TWELVE_DEGREES_IN_RAD = (12 / 180) * math.pi


class CartPoleEnv(object):
    """
    Class extracting common logic for JModelica and Dymola environments for CartPole experiments.
    Allows to avoid code duplication.
    Implements all methods for connection to the OpenAI Gym as an environment.


    """

    # modelicagym API implementation
    def _is_done(self):
        """
        Internal logic that is utilized by parent classes.
        Checks if cart position or pole angle are inside required bounds, defined by thresholds:
        x_threshold - 2.4
        angle threshold - 12 degrees

        :return: boolean flag if current state of the environment indicates that experiment has ended.
        True, if cart is not further than 2.4 from the starting point
        and angle of pole deflection from vertical is less than 12 degrees
        """
        x, x_dot, theta, theta_dot = self.state
        logger.debug("x: {0}, x_dot: {1}, theta: {2}, theta_dot: {3}".format(x, x_dot, theta, theta_dot))

        theta = abs(theta - NINETY_DEGREES_IN_RAD)

        if abs(x) > self.x_threshold:
            done = True
        elif theta > self.theta_threshold:
            done = True
        else:
            done = False

        return done

    def _get_action_space(self):
        """
        Internal logic that is utilized by parent classes.
        Returns action space according to OpenAI Gym API requirements

        :return: Discrete action space of size 2, as only 2 actions are available: push left or push right.
        """
        return spaces.Discrete(2)

    def _get_observation_space(self):
        """
        Internal logic that is utilized by parent classes.
        Returns observation space according to OpenAI Gym API requirements

        :return: Box state space with specified lower and upper bounds for state variables.
        """
        high = np.array([self.x_threshold, np.inf, self.theta_threshold, np.inf])
        return spaces.Box(-high, high)

    # OpenAI Gym API implementation
    def step(self, action):
        """
        OpenAI Gym API. Executes one step in the environment:
        in the current state perform given action to move to the next action.
        Applies force of the defined magnitude in one of two directions, depending on the action parameter sign.

        :param action: alias of an action to be performed. If action > 0 - push to the right, else - push left.
        :return: next (resulting) state
        """
        action = self.force if action > 0 else -self.force
        return super(CartPoleEnv,self).step(action)

    # This function was heavily inspired by OpenAI example:
    # https://github.com/openai/gym/blob/master/gym/envs/classic_control/cartpole.py
    def render(self, mode='human', close=False):
        """
        OpenAI Gym API. Determines how current environment state should be rendered.
        Draws cart-pole with the built-in gym tools.

        :param mode: rendering mode. Read more in Gym docs.
        :param close: flag if rendering procedure should be finished and resources cleaned.
        Used, when environment is closed.
        :return: rendering result
        """
        pass

    def close(self):
        """
        OpenAI Gym API. Closes environment and all related resources.
        Closes rendering.
        :return: True if everything worked out.
        """
        return self.render(close=True)


class JModelicaCSCartPoleEnv(CartPoleEnv, FMI2CSEnv):
    """
    Wrapper class for creation of cart-pole environment using JModelica-compiled FMU (FMI standard v.2.0).

    Attributes:
        m_cart (float): mass of a cart.

        m_pole (float): mass of a pole.

        theta_0 (float): angle of the pole, when experiment starts.
        It is counted from the positive direction of X-axis. Specified in radians.
        1/2*pi means pole standing straight on the cast.

        theta_dot_0 (float): angle speed of the poles mass center. I.e. how fast pole angle is changing.
        time_step (float): time difference between simulation steps.
        positive_reward (int): positive reward for RL agent.
        negative_reward (int): negative reward for RL agent.
    """

    def __init__(self,
                 m_cart,
                 m_pole,
                 theta_0,
                 theta_dot_0,
                 time_step,
                 positive_reward,
                 negative_reward,
                 force,
                 log_level,
                 fmu_result_handling='memory',
                 fmu_result_ncp=100.,
                 filter_flag=False):

        logger.setLevel(log_level)

        self.force = force
        self.theta_threshold = TWELVE_DEGREES_IN_RAD
        self.x_threshold = 2.4

        self.viewer = None
        self.display = None
        self.pole_transform = None
        self.cart_transform = None

        config = {
            'model_input_names': ['f'],
            'model_output_names': ['x', 'x_dot', 'theta', 'theta_dot'],
            'model_parameters': {'m_cart': m_cart, 'm_pole': m_pole,
                                 'theta_0': theta_0, 'theta_dot_0': theta_dot_0},
            'initial_state': (0, 0, 85 / 180 * math.pi, 0),
            'time_step': time_step,
            'positive_reward': positive_reward,
            'negative_reward': negative_reward,
            'fmu_result_handling':fmu_result_handling,
            'fmu_result_ncp':fmu_result_ncp,
            'filter_flag':filter_flag
        }
        # specify fmu path and model
        fmu_path = os.path.dirname(os.path.realpath(__file__))
        super(JModelicaCSCartPoleEnv,self).__init__(os.path.join(fmu_path,"ModelicaGym_CartPole.fmu"),
                         config, log_level)