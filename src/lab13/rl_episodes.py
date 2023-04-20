'''
Lab 13: My first AI agent.
In this lab, you will create your first AI agent.
You will use the run_episode function from lab 12 to run a number of episodes
and collect the returns for each state-action pair.
Then you will use the returns to calculate the action values for each state-action pair.
Finally, you will use the action values to calculate the optimal policy.
You will then test the optimal policy to see how well it performs.

Sidebar-
If you reward every action you may end up in a situation where the agent
will always choose the action that gives the highest reward. Ironically,
this may lead to the agent losing the game.
'''
import sys
from pathlib import Path

# line taken from turn_combat.py
sys.path.append(str((Path(__file__) / ".." / "..").resolve().absolute()))

from lab11.pygame_combat import PyGameComputerCombatPlayer
from lab11.turn_combat import CombatPlayer
from lab12.episode import run_episode

from collections import defaultdict
import random
import numpy as np


class PyGameRandomCombatPlayer(PyGameComputerCombatPlayer):
    def __init__(self, name):
        super().__init__(name)

    def weapon_selecting_strategy(self):
        self.weapon = random.randint(0, 2)
        return self.weapon


class PyGamePolicyCombatPlayer(CombatPlayer):
    def __init__(self, name, policy):
        super().__init__(name)
        self.policy = policy

    def weapon_selecting_strategy(self):
        self.weapon = self.policy[(self.health, self.current_env_state[0])]
        #self.weapon = self.policy[self.current_env_state]
        return self.weapon


def run_random_episode(player, opponent):
    player.health = random.choice(range(10, 110, 10))
    opponent.health = random.choice(range(10, 110, 10))
    return run_episode(player, opponent)


def get_history_returns(history):
    total_return = sum([reward for _, _, reward in history])
    returns = {}
    for i, (state, action, reward) in enumerate(history):
        if state not in returns:
            returns[state] = {}
        returns[state][action] = total_return - sum(
            [reward for _, _, reward in history[:i]]
        )
    return returns


##def run_episodes(n_episodes):
 #   ''' Run 'n_episodes' random episodes and return the action values for each state-action pair.
 #       Action values are calculated as the average return for each state-action pair over the 'n_episodes' episodes.
 #       Use the get_history_returns function to get the returns for each state-action pair in each episode.
 #       Collect the returns for each state-action pair in a dictionary of dictionaries where the keys are states and
 #           the values are dictionaries of actions and their returns.
 #       After all episodes have been run, calculate the average return for each state-action pair.
 #       Return the action values as a dictionary of dictionaries where the keys are states and 
 #           the values are dictionaries of actions and their values.
 #   '''
 #   episodeReturns = []
 #   
 #   for i in range(n_episodes):
 #       episodeReturns.append(get_history_returns(run_episode(PyGameRandomCombatPlayer("Player1"), PyGameComputerCombatPlayer("Player2"), False)))
 #   
 #   returnsSum = {}
 #   for ret in episodeReturns:
 #       for state in ret:
 #           if state not in returnsSum: 
 #                   returnsSum[state] = {}
 #           for action in ret[state]:
 #               if action not in returnsSum[state]: 
 #                   returnsSum[state][action] = {"value": 0, "num": 0}
 #               returnsSum[state][action]["value"] += ret[state][action]
 #               returnsSum[state][action]["num"] += 1
 #   
 #   action_values = {}
 #   for state in returnsSum:
 #       if state not in action_values:
 #           action_values[state] = {}
 #       for action in returnsSum[state]:
 #           action_values[state][action] = returnsSum[state][action]["value"] / returnsSum[state][action]["num"]
 #       
 #   return action_values

def run_episodes(n_episodes):
    # Action values format: {(PlayerHealth, EnemyHealth): {PlayerWeapon: Reward}, (): {}, (): {},...}
    # This is a dictionary of dictionaries where keys are states and values are dictionaries of actions and their returns
    action_values_unaveraged = {}
    action_values_averaged = {}
    for episode in range(n_episodes):
        player = PyGameRandomCombatPlayer("PLAYER AI")
        opponent = PyGameComputerCombatPlayer("OPPONENT AI")

        # Grab the episode history (healths, actions, and rewards) for each turn in a combat
        history = run_episode(player, opponent)

        # This appends the history to the action_values dictionary
        ##action_values_unaveraged.update(get_history_returns(history))
        returns = get_history_returns(history)

        # Checks for duplicates in the history
        for state in returns:
            if state not in action_values:
                action_values_unaveraged.update({state : [returns[state]]})
            else:
                action_values_unaveraged[state].append(returns[state])
        
        '''For each state in the action_values_unaveraged, add up all of the rewards a specific action took and get
          the average of it. After that store all of the averages in an action_values dictionary. 
          
          Example:
            Unaveraged: (100, 90): {0: -1, 1: 3, 1: 3, 1: 3, 2: 0, 2: -1}   #note that reward will not be 3 but is to simplify example
            Averaged:   (100, 90): {0: -1, 1: 3, 2: -0.5}                   #this is what I want
        '''

        print("\n\n\n")
        print(action_values_unaveraged)


    print("\n\n\n")
    print(action_values_unaveraged)
    print("\n\n\n")
    print("\n\n\n")

    for state in action_values_unaveraged:
        weaponTotal_0 = 0
        weaponTotal_1 = 0
        weaponTotal_2 = 0
        weaponCount_0 = 0
        weaponCount_1 = 0
        weaponCount_2 = 0

        for dictlist in action_values_unaveraged[state]:
            if 0 in dictlist:
                weaponTotal_0 += float(dictlist[0])
                weaponCount_0 += 1
            if 1 in dictlist:
                weaponTotal_1 += float(dictlist[1])
                weaponCount_1 += 1
            if 2 in dictlist:
                weaponTotal_2 += float(dictlist[2])
                weaponCount_2 += 1
        # Prevents divide by 0
        if weaponCount_0 == 0:
            weaponCount_0 =1
        if weaponCount_1 == 0:
            weaponCount_1 = 1
        if weaponCount_2 == 0:
            weaponCount_2 = 1
            
        action_values_averaged.update({state:{0:weaponTotal_0/weaponCount_0, 1:weaponTotal_1/weaponCount_1, 2:weaponTotal_2/weaponCount_2}})
    
    print("\n\n\n")
    print(action_values_averaged)
    print("\n\n\n")
    print("\n\n\n")
    return action_values_averaged

def get_optimal_policy(action_values):
    optimal_policy = defaultdict(int)
    for state in action_values:
        optimal_policy[state] = max(action_values[state], key=action_values[state].get)
    return optimal_policy


def test_policy(policy):
    names = ["Legolas", "Saruman"]
    total_reward = 0
    for _ in range(100):
        player1 = PyGamePolicyCombatPlayer(names[0], policy)
        player2 = PyGameComputerCombatPlayer(names[1])
        players = [player1, player2]
        total_reward += sum(
            [reward for _, _, reward in run_episode(*players,printOutput=True)]
        )
    return total_reward / 100


if __name__ == "__main__":
    action_values = run_episodes(2000)
    print("Action values" + str(action_values))
    optimal_policy = get_optimal_policy(action_values)
    print("Optimal policy" + str(optimal_policy))
    print(test_policy(optimal_policy))
3