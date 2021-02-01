from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col

#11 columns of 7 rows, can move from 1st column to 11th column and 1st row to 7th row.
#Minimum of 2 food units on board at all times.
#Every 40 steps goose loses segment.
#The reward is calculated as the current turn + goose length.
#Surviving agents at the end of the episode receive maximum reward as (2 * episode steps) + length.
#200 steps each turn.
#Surviving agents receive maximum reward 2∗configuration.episodeSteps.

#Don't know who survives in head on collisions?

numCols = 11
numRows = 7

def agent(obs_dict, config_dict):
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

def agent2(obs_dict, config_dict):
    """This agent always moves toward observation.food[0] but does not take advantage of board wrapping"""
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    #player_goose is list of all bodypart positions
    player_head = player_goose[0]
    player_row, player_column = row_col(player_head, configuration.columns)

    #will replace player_row, player_column with 2d array that has all positions filled with all player information
    food, food_row, food_column = which_food(observation, configuration, player_row, player_column)
    

    if food_row > player_row:
        return Action.SOUTH.name
    if food_row < player_row:
        return Action.NORTH.name
    if food_column > player_column:
        return Action.EAST.name
    return Action.WEST.name

def which_food(observation, configuration, player_row, player_column):
    #instead of using obeservation.food[0] should find out which food has shortest route from head.
    
    minRows = numRows
    minCols = numCols
    minSum = 0

    for i in range(len(observation.food)):
        tempfood = observation.food[i]
        tempfood_row, tempfood_column = row_col(tempfood, configuration.columns)
        tempRowDist = min_distance_dircular_dist(numRows, player_row, tempfood_row)
        tempColDist = min_distance_dircular_dist(numCols, player_column, tempfood_column)
        if (tempRowDist + tempColDist) > (minRows + minCols):
            minRows = tempRowDist
            minCols = tempColDist
            minSum = i

    food = observation.foor[minSum]
    food_row, food_column = row_col(food, configuration.columns)

    #This will need to be changed, food distance depends on direction snake just traveled, whether other geese are close (as it could be pointless) and which spots on the board are filled
    #Will implement a map solving algorithm for all alive geese and if our goose has shortest distance, will select food that way.
    
    #Could also implement escape route algorithm? Don't know how that would work, ask ben

    return food, food_row, food_column

def min_distance_dircular_dist(lenList, index1, index2):
    tempDist = abs(index1 - index2)
    minDistance = min(lenList-tempDist, tempDist)
    return minDistance