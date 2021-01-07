# -*- coding: utf-8 -*-
'''This example is from https://github.com/ucuapps/modelicagym, and modified for python 2 and for docker implementation.
'''
from __future__ import print_function
from __future__ import absolute_import, division

import logging
from q_learning import QLearner
import gym
import numpy as np
import math
import time

def cart_pole_train_qlearning(cart_pole_env, max_number_of_steps=500, n_episodes=4, visualize=True):
    """
    Runs one experiment of Q-learning training on cart pole environment
    :param cart_pole_env: environment RL agent will learn on.
    :param max_number_of_steps: maximum episode length.
    :param n_episodes: number of episodes to perform.
    :param visualize: flag if experiments should be rendered.
    :return: trained Q-learning agent, array of actual episodes length, execution time in s
    """

    start = time.time()
    n_outputs = cart_pole_env.observation_space.shape[0]

    episode_lengths = np.array([])

    #bins of observation space - state space
    x_bins = _get_bins(-2.4, 2.4, 10)
    x_dot_bins = _get_bins(-1, 1, 10)
    phi_bins = _get_bins(78/180*math.pi, 102/180*math.pi, 10)
    phi_dot_bins = _get_bins(-2, 2, 10)

    learner = QLearner(n_states=10 ** n_outputs,
                       n_actions=cart_pole_env.action_space.n,
                       learning_rate=0.2,
                       discount_factor=1,
                       exploration_rate=0.5,
                       exploration_decay_rate=0.99)

    for episode in range(n_episodes):
        x, x_dot, phi, phi_dot = cart_pole_env.reset()

        state = _get_state_index([_to_bin(x, x_bins),
                                  _to_bin(phi, phi_bins),
                                  _to_bin(x_dot, x_dot_bins),
                                  _to_bin(phi_dot, phi_dot_bins)])

        action = learner.set_initial_state(state)

        for step in range(max_number_of_steps):
            if visualize:
                cart_pole_env.render()

            observation, reward, done, _ = cart_pole_env.step(action)

            x, x_dot, phi, phi_dot = observation
            state_prime = _get_state_index([_to_bin(x, x_bins),
                                            _to_bin(phi, phi_bins),
                                            _to_bin(x_dot, x_dot_bins),
                                            _to_bin(phi_dot, phi_dot_bins)])

            action = learner.learn_observation(state_prime, reward)

            if done or step == max_number_of_steps - 1:
                episode_lengths = np.append(episode_lengths, int(step + 1))
                break
    end = time.time()
    execution_time = end - start
    return learner, episode_lengths, execution_time


# Internal logic for state discretization
def _get_bins(lower_bound, upper_bound, n_bins):
    """
    Given bounds for environment state variable splits it into n_bins number of bins,
    taking into account possible values outside the bounds.

    :param lower_bound: lower bound for variable describing state space
    :param upper_bound: upper bound for variable describing state space
    :param n_bins: number of bins to receive
    :return: n_bins-1 values separating bins. I.e. the most left bin is opened from the left,
    the most right bin is open from the right.
    """
    return np.linspace(lower_bound, upper_bound, n_bins + 1)[1:-1]


def _to_bin(value, bins):
    """
    Transforms actual state variable value into discretized one,
    by choosing the bin in variable space, where it belongs to.

    :param value: variable value
    :param bins: sequence of values separating variable space
    :return: number of bin variable belongs to. If it is smaller than lower_bound - 0.
    If it is bigger than the upper bound
    """
    return np.digitize(x=[value], bins=bins)[0]


def _get_state_index(state_bins):
    """
    Transforms discretized environment state (represented as sequence of bin indexes) into an integer value.
    Value is composed by concatenating string representations of a state_bins.
    Received string is a valid integer, so it is converted to int.

    :param state_bins: sequence of integers that represents discretized environment state.
    Each integer is an index of bin, where corresponding variable belongs.
    :return: integer value corresponding to the environment state
    """
    state = int("".join(map(lambda state_bin: str(state_bin), state_bins)))
    return state


def run_ql_experiments(n_experiments=1,
                       n_episodes=10,
                       visualize=False,
                       m_cart=10,
                       m_pole=1,
                       theta_0=85/180*math.pi,
                       theta_dot_0=0,
                       time_step=0.05,
                       positive_reward=1,
                       negative_reward=-100,
                       force=12,
                       log_level=logging.DEBUG):
    """
    Wrapper for running experiment of q-learning training on cart pole environment.
    Is responsible for environment creation and closing, sets all necessary parameters of environment.
    Runs n exepriments, where each experiment is training Q-learning agent on the same environment.
    After one agent finished training, environment is reset to the initial state.
    Parameters of the experiment:
    :param n_episodes: number of episodes to perform in each experiment run
    :param visualize: boolean flag if experiments should be rendered
    :param n_experiments: number of experiments to perform.
    :param log_level: level of logging that should be used by environment during experiments.
    :param force: magnitude to be applied during experiment at each time step.

    Parameters of the cart pole environment:
    :param m_cart: mass of cart.
    :param m_pole: mass of a pole.
    :param theta_0: angle of the pole. Is counted from the positive direction of X-axis. Specified in radians.
    1/2*pi means pole standing straight on the cast.
    :param theta_dot_0: angle speed of the poles mass center. I.e. how fast pole angle is changing.
    :param time_step: time difference between simulation steps.
    :param positive_reward: positive reward for RL agent.
    :param negative_reward: negative reward for RL agent.
    :return: trained Q-learning agent, array of actual episodes length
    that were returned from cart_pole_train_qlearning()
    """
    config = {
        'm_cart': m_cart,
        'm_pole': m_pole,
        'theta_0': theta_0,
        'theta_dot_0': theta_dot_0,
        'time_step': time_step,
        'positive_reward': positive_reward,
        'negative_reward': negative_reward,
        'force': force,
        'log_level': log_level
    }

#    from gym.envs.registration import register
    import gym_cart_jmodelica
    env_name = "JModelicaCSCartPoleEnv-v0"

#    register(
#        id=env_name,
#        entry_point='examples:JModelicaCSCartPoleEnv',
#        kwargs=config
#    )
    trained_agent_s =[]
    episodes_length_s = []
    exec_time_s = []
    # env = gym.make(env, some_kwarg=your_vars)
    # need find a way to update the configuration at one time
    env = gym.make(env_name,
        m_cart=m_cart,
        m_pole=m_pole,
        theta_0=theta_0,
        theta_dot_0=theta_dot_0,
        time_step=time_step,
        positive_reward=positive_reward,
        negative_reward=negative_reward,
        force=force,
        log_level=log_level)
        
    for i in range(n_experiments):
        trained_agent, episodes_length, exec_time = cart_pole_train_qlearning(env,
                                                                              n_episodes=n_episodes,
                                                                              visualize=visualize)
        trained_agent_s.append(trained_agent)
        episodes_length_s.append(episodes_length)
        exec_time_s.append(exec_time)
        env.reset()

    env.close()
    # delete registered environment to avoid errors in future runs.
    # del gym.envs.registry.env_specs[env_name]
    return trained_agent_s, episodes_length_s, exec_time_s


#if __name__ == "__main__":
#    _, episodes_lengths, exec_times = run_ql_experiments(visualize=True, log_level=logging.INFO)
#    print("Experiment length {} s".format(exec_times[0]))
#    print(u"Avg episode performance {} {} {}".format(episodes_lengths[0].mean(),
#                                                     chr(177),  # plus minus sign
#                                                     episodes_lengths[0].std()))
#    print(u"Max episode performance {}".format(episodes_lengths[0].max()))
#    print(u"All episodes performance {}".format(episodes_lengths))

def run_experiment_with_result_files(folder,
                                     n_experiments,
                                     n_episodes,
                                     visualize,
                                     m_cart,
                                     m_pole,
                                     theta_0,
                                     theta_dot_0,
                                     time_step,
                                     positive_reward,
                                     negative_reward,
                                     force,
                                     log_level):
    """
    Runs experiments with the given configuration and writes episodes length of all experiment as one file
    and execution times of experiments as another.
    File names are composed from numerical experiment parameters
    in the same order as in function definition.
    Episodes length are written as 2d-array of shape (n_episodes, n_experiments):
    i-th row - i-th episode, j-th column - j-th experiment.

    Execution times are written as 1d-array of shape (n_experiments, ): j-th element - j-th experiment


    :param folder: folder for experiment result files
    :return: None
    """
    experiment_file_name_prefix = "{}/experiment_{}_{}_{}_{}_{:.0f}_{}_{}_{}_{}_{}_".format(
        folder,
        n_experiments,
        n_episodes,
        m_cart,
        m_pole,
        theta_0 * 180 / math.pi,
        theta_dot_0,
        time_step,
        positive_reward,
        negative_reward,
        force
    )
    _, episodes_lengths, exec_times = run_ql_experiments(n_experiments=n_experiments,
                                                         n_episodes=n_episodes,
                                                         visualize=visualize,
                                                         m_cart=m_cart,
                                                         m_pole=m_pole,
                                                         theta_0=theta_0,
                                                         theta_dot_0=theta_dot_0,
                                                         time_step=time_step,
                                                         positive_reward=positive_reward,
                                                         negative_reward=negative_reward,
                                                         force=force,
                                                         log_level=log_level)
    print(episodes_lengths)
    n =experiment_file_name_prefix + "episodes_lengths.csv"
    X = np.transpose(episodes_lengths)
    print(X.shape)
    
    np.savetxt(fname=experiment_file_name_prefix + "episodes_lengths.csv",
               X=np.transpose(episodes_lengths),
               delimiter=",",
               fmt='%10.4f')
    np.savetxt(fname=experiment_file_name_prefix + "exec_times.csv",
               X=np.array(exec_times),
               delimiter=",",
               fmt='%10.4f')



def reward_ratio_experiment(rws):
    for pos_rew, neg_rew in rws:
        run_experiment_with_result_files(folder,
                                         n_experiments=1,
                                         n_episodes=200,
                                         visualize=False,
                                         m_cart=10,
                                         m_pole=1,
                                         theta_0=85 / 180 * math.pi,
                                         theta_dot_0=0,
                                         time_step=0.05,
                                         positive_reward=pos_rew,
                                         negative_reward=neg_rew,
                                         force=15,
                                         log_level=logging.INFO)


if __name__ == "__main__":
    import time
    import os
    
    start = time.time()
    folder = "experiments_results"
    if not os.path.exists(folder):
        os.mkdir(folder)
    # following experiments rake significant amount of time, so it is advised to run only one of them at once
    reward_ratio_experiment([[1, -100], [1, -50], [1, -200],])
    end = time.time()
    print("Total execution time {:.2f} seconds".format(end-start))
