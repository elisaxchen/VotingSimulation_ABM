#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 16:09:35 2021

@author: elisaxchen
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from .agents import Voter, PollingLocation
from .model import Voting #F0AFA8

color_dic = {3: "#FF8BA0", 2: "#FFA8B5", 1: "#F0AFA8"}


def Voter_portrayal(agent):
    '''
    Generates a dictionary of characteristics related to the portrayal of
    voters and polling locations.
    '''
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Voter:
        # portray agents as brown circles
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.75
        portrayal["Filled"] = "true"
        if agent.speed == 1: # poor agents
            portrayal["Color"] = ["#FF7F0E"]
        if agent.speed == 3: # middle class agents
            portrayal["Color"] = ["#2CA02C"]
        if agent.speed ==6: # rich agents
            portrayal["Color"] = ["#1F77B4"]
        portrayal["Layer"] = 1

    elif type(agent) is PollingLocation:
        # portray voting machine as shades of red, depending on whether is occupied or not
        if agent.amount != 0:
            portrayal['Shape'] = "icon.png"
            portrayal['scale'] = 0.95
            #portrayal["Color"] = color_dic[agent.amount] #dark red, available machine
        else:
            portrayal["Color"] = "#FFFFFF" #light red, already in use
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
            portrayal["w"] = 1
            portrayal["h"] = 1
        portrayal["Layer"] = 0

    return portrayal

# construct a grid with agents portrayed based on SsAgent_portrayal function
# above, along with a chart that tracks the number of living agents at each
# time step (automatically updates with data from datacollector):

canvas_element = CanvasGrid(Voter_portrayal, 50, 50, 500, 500)
chart_voters = ChartModule([{"Label": "Disenfranchised Voters", "Color": "#AA0000"}])

chart_speed = ChartModule([
    {'Label': 'Poor', 'Color': '#FF7F0E'}, 
    {'Label': 'Middle Class', 'Color': '#2CA02C'},
    {'Label': 'Rich', 'Color': '#1F77B4'}])

server = ModularServer(
    Voting, [canvas_element, chart_voters, chart_speed], "Voting Simulation"
)
