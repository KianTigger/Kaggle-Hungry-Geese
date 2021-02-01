from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col

#11 columns of 7 rows, can move from 1st column to 11th column and 1st row to 7th row.
#Minimum of 2 food units on board at all times.
#Every 40 steps goose loses segment.
#The reward is calculated as the current turn + goose length.
#Surviving agents at the end of the episode receive maximum reward as (2 * episode steps) + length.
#200 steps each turn.
#Surviving agents receive maximum reward 2∗configuration.episodeSteps.

#They both die, but the shorter one dies first. If it's down to the last two geese and your's is longer, 
# a head-on collision will end the game with you in first place.
#Not sure if this helps too much


#Need to think of a good way to incorporate last move for our goose and others geese as it's important in determining smallest steps to get to food etc.


numCols = 11
numRows = 7
Matrix = [[0 for numCols in range(numCols)] for numRows in range(numRows)]

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

def fill_matrix(observation, configuration):
    #0 = empty space
    #1 = player head
    #2 = player body
    #3 = generic goose head
    #4 = generic goose body
    #5 = food
    foodPosition = 5
    player_index = observation.index
    for i in range(len(observation.geese)):
        #Checks if for our goose or generic goose
        if i == player_index:
            bodyPart = 2
            headPart = 1
        else:
            bodyPart = 4
            headPart = 3
        player_goose = observation.geese[i]
        #for each body part
        for j in range(len(player_goose)):
            player_part = player_goose[j]
            player_row, player_column = row_col(player_part, configuration.columns)
            if j == 0:
                Matrix[player_row][player_column] = headPart
            else:
                Matrix[player_row][player_column] = bodyPart

    #Food placement
    for i in range(len(observation.food)):
        tempfood = observation.food[i]
        tempfood_row, tempfood_column = row_col(tempfood, configuration.columns)
        Matrix[tempfood_row][tempfood_column] = foodPosition
    



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