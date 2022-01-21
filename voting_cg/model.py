#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 14:15:00 2021

@author: elisaxchen
"""

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


from .agents import Voter, PollingLocation
from .schedule import RandomActivationByBreed

# Here are the numbers we'd like to collect: number of rich / middle class 
# and poor agents being disfranchaised. 

def get_num_rich_agents(model):
    """return number of rich agents"""

    rich_agents = [a for a in model.schedule.agents if a.speed == 6]
    return len(rich_agents)


def get_num_poor_agents(model):
    """return number of poor agents"""

    poor_agents = [a for a in model.schedule.agents if a.speed == 1]
    return len(poor_agents)

def get_num_mid_agents(model):
    """return number of middle agents"""

    middle_agents = [a for a in model.schedule.agents if a.speed == 3]
    return len(middle_agents)


def total_disenfranchised(model):
    """sum of all disenfranchised voters"""

    rich = get_num_rich_agents(model)
    poor = get_num_poor_agents(model)
    mid = get_num_mid_agents(model)
    return rich + poor + mid

def pc_disenfranchised(model):
    """percent of all disenfranchised voters"""

    tot = total_disenfranchised(model)
    initial_voters = model.initial_voters
    return tot/initial_voters

def pc_disenfranchised_poor(model):
    """percent of poor disenfranchised voters"""

    tot_poor = get_num_poor_agents(model)
    initial_voters = model.initial_voters
    ini_poor = initial_voters * 0.6
    return tot_poor / ini_poor

def pc_disenfranchised_mid(model):
    """percent of mid disenfranchised voters"""

    tot_mid = get_num_mid_agents(model)
    initial_voters = model.initial_voters
    ini_mid = initial_voters * 0.3
    return tot_mid / ini_mid

def pc_disenfranchised_rich(model):
    """percent of rich disenfranchised voters"""

    tot_rich = get_num_rich_agents(model)
    initial_voters = model.initial_voters
    ini_rich = initial_voters * 0.1
    return tot_rich / ini_rich

# there are 116 voting machines in the grid 
def num_machines_per100(model): 
    initial_voters = model.initial_voters
    return int(116 / initial_voters * 100)


class Voting(Model):
    """
    Voting Simulation
    """

    #verbose = True  # Print-monitoring

    def __init__(self, height=50, width=50, initial_voters=500, verbose=False):
        """
        Create a new Constant Growback model with the given parameters.

        Args:
            initial_voters: Number of voters to start with
        """

        # Set parameters
        self.height = height
        self.width = width
        self.initial_voters = initial_voters
        self.verbose = verbose
        
        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)

        # collect data throughout simulation on the number of disfranchised voted
        # at each time step
        self.datacollector = DataCollector(
            model_reporters={
                "Rich": get_num_rich_agents,
                "Poor": get_num_poor_agents,
                "Middle Class": get_num_mid_agents,
                "Disenfranchised Voters": lambda m: m.schedule.get_breed_count(Voter),
             })
        

        # When a voting machine is available, which is when one human agent 
        # finishes casting their vote, we set it back to 1. 
        # pre-defined voting machine locations can be found at pollinglocation-map.txt
        machine_distribution = np.genfromtxt("voting_cg/pollinglocation_map.txt")
        for _, x, y in self.grid.coord_iter():
            # set max vm to pre-defined amount
            max_votingmachines = machine_distribution[x, y]
            machine = PollingLocation((x, y), self, max_votingmachines)

            # place voting machines on the grid and add it to the schedule
            self.grid.place_agent(machine, (x, y))
            self.schedule.add(machine)
          
        # Create voters with vision = 10, different speeds (1,2,4)
        chosen_already = set([])
        for i in range(self.initial_voters):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            while (x,y) in chosen_already:
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
        
            chosen_already.add((x,y))
            vision = 10 # set a fixed vision 
            speed = self.random.choices([1,3,6], weights=[.6, .3, .1], k=1)[0]
            voter_agent = Voter((x, y), self, False, vision, speed)

            # place agent at a random location in the grid to start and add to
            # schedule
            self.grid.place_agent(voter_agent, (x, y))
            self.schedule.add(voter_agent)

        self.running = True
        self.datacollector.collect(self)

            
    def step(self):
        self.schedule.step()

        # collect data after each step on how many agents do not vote yet
        self.datacollector.collect(self)

        if self.verbose:
            print([self.schedule.time, self.schedule.get_breed_count(Voter)])

    def run_model(self, step_count=200):
        '''
        Run model over a set number of steps (e.g. 200) and report number of
        agents at the beginning and end of simulation (if verbose is
        uncommented at the beginning of the code)
        '''
        if self.verbose:
            print(
                "Initial number of Voters: ",
                self.schedule.get_breed_count(Voter),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print(
                "Disfranchised Voters: ",
                self.schedule.get_breed_count(Voter),
            )
