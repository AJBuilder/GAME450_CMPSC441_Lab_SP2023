'''
Lab 4: Rock-Paper-Scissor AI Agent

In this lab you will build one AI agent for the game of Rock-Paper-Scissors, that can defeat a few different kinds of 
computer players.

You will update the AI agent class to create your first AI agent for this course.
Use the precept sequence to find out which opponent agent you are facing, 
so that it can beat these three opponent agents:

    Agent Single:  this agent picks a weapon at random at the start, 
                   and always plays that weapon.  
                   For example: 2,2,2,2,2,2,2,.....

    Agent Switch:  this agent picks a weapon at random at the start,
                   and randomly picks a weapon once every 10 rounds.  
                   For example:  2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,...

    Agent Mimic:  this agent picks a weapon at random in the first round, 
                  and then always does what you did the previous round.  
                  For example:  if you played 1,2,0,1,2,0,1,2,0,...  
                   then this agent would play 0,1,2,0,1,2,0,1,2,...

Discussions in lab:  You don't know ahead of time which opponent you will be facing, 
so the first few rounds will be used to figure this out.   How?

Once you've figured out the opponent, apply rules against that opponent. 
A model-based reflex agent uses rules (determined by its human creator) to decide which action to take.

If your AI is totally random, you should be expected to win about 33% of the time, so here is the requirement:  
In 100 rounds, you should consistently win at least 85 rounds to be considered a winner.

You get a 0 point for beating the single agent, 1 points for beating the switch agent, 
and 4 points for beating the mimic agent.

'''

from rock_paper_scissor import Player
from rock_paper_scissor import run_game
from rock_paper_scissor import random_weapon_select

class AiPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.initial_weapon = random_weapon_select()
        
    
    def weapon_selecting_strategy(self):
        history = min(len(self.opponent_choices), 15)
        single = 0
        switch = 0
        mimic = 0
        
        if history > 0:
            
            # Score Single
            for i in range(-history, 0):
                if self.opponent_choices[i] == self.opponent_choices[-1]:
                    single += 1
                else:
                    single = 0
                    break
            
            # Score Switch
            compIndex = -history
            diffNum = 1
            thisNum = 0
            for i in range(-history, 0):
                if self.opponent_choices[compIndex] == self.opponent_choices[i]:
                    switch += 1
                    thisNum += 1
                else:
                    if diffNum == 3:
                        switch = 0
                        break
                    diffNum += 1
                    switch += 1
                    thisNum = 0
                    compIndex = i
                 
            # Score Mimic
            if history != 1:
                for i in range(1, history):
                    if self.opponent_choices[-i] == self.my_choices[-i-1]:
                        mimic += 1
                    else:
                        mimic = 0
                        break
            else:
                mimic = 0
            
            print(self.opponent_choices)            
                
            print("Single Score: " + str(single))
            print("Switch Score: " + str(switch))
            print("Mimic Score: " + str(mimic))
            
            if single >= switch and single >= mimic:
                return (self.opponent_choices[-1] + 1) % 3 # Select weapon that would beat last choice
            
            if switch > single and switch > mimic:
                lastTen = min(len(self.opponent_choices), 10)
                if self.opponent_choices[-lastTen:].count(self.opponent_choices[-1]) == 10:
                    return random_weapon_select() # Weapon is going to change, so pick new weapon
                else:
                    return (self.opponent_choices[-1] + 1) % 3
                
            if mimic > single and mimic > switch:
                return (self.my_choices[-1] + 1) % 3 # Pick to beat my last weapon
        
        return random_weapon_select() # If no clue, random weapon


if __name__ == '__main__':
    final_tally = [0]*3
    for agent in range(3):
        for i in range(100):
            tally = [score for _, score in run_game(AiPlayer("AI"), 100, agent)]
            if sum(tally) == 0:
                final_tally[agent] = 0
            else:
                final_tally[agent] += tally[0]/sum(tally)

    print("Final tally: ", final_tally)  