#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 12:07:40 2021

@author: elisaxchen
"""

import math
from mesa import Agent

def get_distance(pos_1, pos_2):
    """
    Get the distance between two points.
    Input: pos_1, pos_2: Coordinate tuples for both points.
    Returns: distance between the points
    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)


class Voter(Agent):
    '''
    Voter Agents that move around the grid. Agents are endowed with
    certain random capacities at their construction, vision. All voting status 
    is 0 at the starting point. 
    vote: voting status, 1 represents vote, 0 represents not vote
    vision: the cost of going to the polling location. Some people have the 
    resources to go to the polling location that's far from their neighberhood. 
        
    '''
    def __init__(self, pos, model, moore=False, vision=0, speed = 1):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore
        self.vote = 0 #fixed initial voting status 
        self.vision = vision
        self.speed = speed 
       

    def go_vote(self, pos):
        '''
        Goes to a polling location at a particular cell in the grid.
        '''
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is PollingLocation:
                return agent

    def is_occupied(self, pos):
        '''
        Checks if a cell in the grid is occupied by another human agent
        '''
        this_cell = self.model.grid.get_cell_list_contents([pos])
        if pos == self.pos:
            return False
        else: 
            return len(this_cell) > 1
        

    def move(self):
        '''
        Agent moves to a neighboring cell that has an unoccupied voting machine. 
        In the case of a tie, agent moves to the closest cell. 
        '''
        # Get neighborhood within vision (where cells are unoccupied)
        visible_squres = [i for i in self.model.grid.get_neighborhood(pos=self.pos,
                                                      moore=self.moore,
                                                        include_center=False,
                                                        radius=self.vision)
                     if not self.is_occupied(i)]
        
        neighbors = [i for i in self.model.grid.get_neighborhood(pos=self.pos,
                                                      moore=self.moore,
                                                        include_center=True,
                                                        radius=self.speed)
                     if not self.is_occupied(i)]

        # find closest machine 
        closest_machine = None
        closest_dist = 10000000
        for pos in visible_squres: 
            if self.go_vote(pos).amount == 1: 
                # machine = self.go_vote(pos)
                distance = get_distance(self.pos, pos) 
                if distance < closest_dist: 
                    closest_dist = distance
                    closest_machine = pos
        
        if closest_machine is None: 
            self.random.shuffle(neighbors)
            self.model.grid.move_agent(self, neighbors[0])
            return 
                    
        # find cloest neighbors to the machine 
        cloest_neighbor = None 
        cloest_neigh_dist = 10000000 
        for pos in neighbors: 
            neighbor_dist = get_distance(pos, closest_machine)
            if neighbor_dist < cloest_neigh_dist:
                cloest_neigh_dist = neighbor_dist
                cloest_neighbor = pos 

        self.model.grid.move_agent(self, cloest_neighbor)

    def voted(self):
        '''
        Cast their votes at current location. Updates agent's voting status, 
        which is 1 if they vote and also updates the voting machine, to 0, 
        which means that the current machine is occupied. 
        
        '''
        voting_patch = self.go_vote(self.pos) 
        self.vote = self.vote + voting_patch.amount
        voting_patch.amount = 0

    def step(self):
        '''
        At each step, agents move to a new square in the grid (if it has more
        voting machine than the location they're currently in). 
        They cast their votes at this location.

        If the agent's vote status becomes 1, then they already voted, and we 
        remove them from the simulation. The rest of agents here are disfrenchied. 
        
        '''
        self.move()
        self.voted()
        if self.vote > 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)


class PollingLocation(Agent):
    '''
    The polling locations patches themselves are an agent as well, with a certain maximum
    amount of voting machines (1) available at the location.

    If other agents in the simulation occupy the machine, it will be 0. The machine
    will become 1 per time step as the already voted agents disappear from grid.
    
    '''
    def __init__(self, pos, model, max_votingmachines, speed = 0):
        super().__init__(pos, model)
        self.amount = max_votingmachines
        self.max_votingmachines = max_votingmachines
        self.speed = speed

    def step(self):
        '''
        At each time step, vm is set back to 1 per time step.
        '''
        self.amount = min([self.max_votingmachines, self.amount + 1])
