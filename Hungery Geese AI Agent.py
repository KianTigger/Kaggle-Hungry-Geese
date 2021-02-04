!pip install 'tensorflow==1.15.0'

import random
import numpy as np
import pandas as pd
import tensorflow as tf
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
from gym import spaces


def fill_matrix(observation, configuration):
    #0 = empty space
    #1 = player head
    #2 = player body
    #3 = player end
    #4 = generic goose head
    #5 = generic goose body
    #6 = generic goose end
    #7 = food
    Matrix = [[0 for x in range(numCols)] for y in range(numRows)]
    MatrixNoFood = [[0 for x in range(numCols)] for y in range(numRows)]
    MatrixHeadAvoid1 = [[0 for x in range(numCols)] for y in range(numRows)]
    MatrixHeadAvoid2 = [[0 for x in range(numCols)] for y in range(numRows)]

    foodPosition = 7
    player_index = observation.index

    #might want to replace non empty spots with an array or tuple (to indicate what it is and what body position to track all parts of goose neck.)
    
    for i in range(len(observation.geese)):
        #Checks if for our goose or generic goose
        if i == player_index:
            bodyPart = 2
            headPart = 1
            endPart = 3
        else:
            bodyPart = 5
            headPart = 4
            endPart = 6
        player_goose = observation.geese[i]
        #for each body part
        for j in range(len(player_goose)):
            player_part = player_goose[j]
            player_row, player_column = row_col(player_part, configuration.columns)
            if j == 0:
                Matrix[player_row][player_column] = headPart
                MatrixNoFood[player_row][player_column] = headPart
                #
                MatrixHeadAvoid1[player_row][player_column] = headPart
                MatrixHeadAvoid2[player_row][player_column] = headPart
                
                if i != player_index:
                    for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        node_position = ((player_row + new_position[0])%numRows, (player_column + new_position[1])%numCols)
                        if MatrixHeadAvoid1[node_position[0]][node_position[1]] == 0:
                            MatrixHeadAvoid1[node_position[0]][node_position[1]] = 9
                    for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        node_position = ((player_row + new_position[0])%numRows, (player_column + new_position[1])%numCols)
                        if MatrixHeadAvoid2[node_position[0]][node_position[1]] == 0:
                            MatrixHeadAvoid2[node_position[0]][node_position[1]] = 9
            elif j == len(player_goose)-1:
                Matrix[player_row][player_column] = endPart
                MatrixNoFood[player_row][player_column] = endPart
                #
                MatrixHeadAvoid1[player_row][player_column] = endPart
                MatrixHeadAvoid2[player_row][player_column] = endPart
            else:
                Matrix[player_row][player_column] = bodyPart
                MatrixNoFood[player_row][player_column] = bodyPart
                #
                MatrixHeadAvoid1[player_row][player_column] = bodyPart
                MatrixHeadAvoid2[player_row][player_column] = bodyPart

    #Food placement
    for i in range(len(observation.food)):
        tempfood = observation.food[i]
        tempfood_row, tempfood_column = row_col(tempfood, configuration.columns)
        Matrix[tempfood_row][tempfood_column] = foodPosition
    
    return Matrix, MatrixNoFood, MatrixHeadAvoid1, MatrixHeadAvoid2
    

class GooseGym:
    def __init__(self):
        #actions: up = 0 / / right = 1 // down = 2 // left = 3
        self.action_space = spaces.Discrete(4) #could add func that limits this to allowed moves, or see if training fixes it
        self.observation_space = #could recycle the fill matrix function to make this
    
        


%%writefile submission.py
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
import numpy as np
import time

def agent_ORIGINAL(obs_dict, config_dict):
    """This agent always moves toward observation.food[0] but does not take advantage of board wrapping"""
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    player_head = player_goose[0]
    player_row, player_column = row_col(player_head, configuration.columns)
    food = observation.food[0]
    food_row, food_column = row_col(food, configuration.columns)

    if food_row > player_row:
        return Action.SOUTH.name
    if food_row < player_row:
        return Action.NORTH.name
    if food_column > player_column:
        return Action.EAST.name
    return Action.WEST.name
from kaggle_environments import evaluate, make
env = make("hungry_geese", debug = True)
#env = make("hungry_geese")
env.reset()
env.run(['original.py', 'original.py', 'original.py', 'submission.py'])
#env.run(['submission.py', 'submission.py', 'submission.py', 'submission.py'])
#env.run(['original.py', 'original.py', 'original.py', 'original.py'])

env.render(mode="ipython", width=800, height=700)