#%%writefile submission.py
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
import numpy as np
import time

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


## TO DO LIST ##

#take into account distance other geese have to travel using a* algorithm

#check open spaces around food before distance to see if it is viable ( to stop getting trapped as easily)

#If no suitable food available, a* to our tail, will need to create a matrix without our tail in it, should be relatively trivial.


#overwrites file information
f = open("./myfile1.txt", "w+")
f.write("Starting program")
f.write("\n")
f.close()

f = open("./myfile2.txt", "w+")
f.write("Starting program")
f.write("\n")
f.close()

which_turn = 0

numCols = 11
numRows = 7
Matrix = [[0 for x in range(numCols)] for y in range(numRows)]
MatrixNoFood = [[0 for x in range(numCols)] for y in range(numRows)]
MatrixHeadAvoid1 = [[0 for x in range(numCols)] for y in range(numRows)]
MatrixHeadAvoid2 = [[0 for x in range(numCols)] for y in range(numRows)]

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

    food = observation.food[minSum]
    food_row, food_column = row_col(food, configuration.columns)

    #This will need to be changed, food distance depends on direction snake just traveled, whether other geese are close (as it could be pointless) and which spots on the board are filled
    #Will implement a map solving algorithm for all alive geese and if our goose has shortest distance, will select food that way.
    
    #Could also implement escape route algorithm? Don't know how that would work, ask ben

    return food, food_row, food_column



def which_direction(path):
    f = open("./myfile1.txt", "a")
    f.write("\n")
    f.write("Path passed to which_direction: " + str(path) + "\n")
    f.write("Type of path: " + str(type(path)) + "\n")
    
    if type(path) != list:
        f.write("SOMETHING WENT WRONG AND PATH GOT PASSED THROUGH EVEN THOUGH IT WAS STRING " + "\n")
        return Action.NORTH.name
    try:
        movement = [0, 0]
        movement[0] = path[0][0] - path[1][0]
        movement[1] = path[0][1] - path[1][1]
    except IndexError:
        return Action.NORTH.name
        
    
    f.write("movement chosen")
    f.write(str(movement) + "\n"  + "\n")
    if movement == [1, 0]:
        return Action.NORTH.name
    elif movement == [-1, 0]:
        return Action.SOUTH.name
    elif movement == [0, 1]:
        return Action.WEST.name
    elif movement == [0, -1]:
        return Action.EAST.name
    elif movement == [-6, 0]:
        return Action.NORTH.name
    elif movement == [6, 0]:
        return Action.SOUTH.name
    elif movement == [0, 10]:
        return Action.EAST.name
    elif movement == [0, -10]:
        return Action.WEST.name



def min_distance_dircular_dist(lenList, index1, index2):
    tempDist = abs(index1 - index2)
    minDistance = min(lenList-tempDist, tempDist)
    return minDistance

#for A* algorithm puts goose head in middle  so shortest path is best for circular grid.
def shift_matrix(TempMatrixList, start):
    #Middle position for 11*7 grid is 5, 3
    #start = (player_row, player_column)

    #Easier for steps up with for loop stepsDown = (start[0] - 3 ) * - 1
    stepsUp = ((start[0] + 3 + 1 ) % 7 )
    stepsRight = (start[1] - 5 ) * - 1

    for TempMatrix in TempMatrixList:
        #this code is garbage but I can't think of a good way and np.roll doesn't work for 2d arrays.
        for i in range(stepsUp):
            tempRow = TempMatrix[0]
            for j in range(numRows-1):
                TempMatrix[j] = TempMatrix[j+1]
            TempMatrix[numRows-1] = tempRow

        for j in range(len(TempMatrix)):
            TempMatrix[j] = np.roll(TempMatrix[j], stepsRight)
        #TempMatrix = np.roll(TempMatrix, stepsRight)

    newStart = (3, 5)

    shift = [newStart[0]-start[0],newStart[1]-start[1]]

    return TempMatrixList, newStart, shift




#shift makes geese go down too much?? Oh wait the TempMatrix thing doesn't work need to change that.
#Sometimes infinite loop somewhere, find out where that is!!!
            

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    f = open("./myfile1.txt", "a")
    f.write("\n")
    f.write("\n")
    f.write("STARTING aSTAR ALGORITHM")
    f.write("\n")
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    #np.savetxt('./myfile1.txt', maze, fmt='%s')
    #with open("./myfile2.txt", 'a') as e:
    #    np.savetxt(e, maze,  fmt='%1.3f', newline=", ")
    with open('./myfile2.txt', 'a') as testfile:
        testfile.write("\n")
        for row in maze:
            testfile.write(' '.join([str(a) for a in row]) + '\n')
    
    # Loop until you find the end
    count = 0
    while len(open_list) > 0:
        if count >= 100:
            return "no path"
        count += 1
        f.write("Count: " + str(count) + ", Open_list[0]: " + str(open_list[0]))
        f.write("\n")

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
    return "no path"

def path_to_closest_food(observation, configuration, MatrixsToUse, start, shift):
    #instead of using obeservation.food[0] should find out which food has shortest route from head.
    
    bestFood = 0
    bestFoodDistance = numCols + numRows
    bestPath = "no path"
    f = open("./myfile1.txt", "a")
    for MatrixToUse in MatrixsToUse:
        
        if bestPath != "no path":
            f.write("\n")
            f.write("Current MatrixToUse: " + str(MatrixToUse))
            f.write("\n")
            continue
            
        for i in range(len(observation.food)):
            
            f.write(str(observation.food) + " <-- num foods, ")
            f.write("iteration of path to closest food: " + str(i))
            f.write("\n")
            tempfood = observation.food[i]

            tempfood_row, tempfood_column = row_col(tempfood, configuration.columns)
            end = (tempfood_row, tempfood_column)
            tempRow = int((end[0] + shift[0]) % numRows)
            tempCol = (end[1] + shift[1]) % numCols
            end = (tempRow, tempCol)
            f.write("Start coords2 " + str(start) + "\n" + "End coords2 " + str(end) + "\n")
            filledspaces = 0
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                node_position = ((end[0] + new_position[0])%6, (end[1] + new_position[1])%10)
                if MatrixToUse[node_position[0]][node_position[1]] != 0:
                    if MatrixToUse[node_position[0]][node_position[1]] == 4:
                        filledspaces += 7
                        f.write("Head detected")
                    filledspaces += 1
            if filledspaces <= 1:
                path = astar(MatrixToUse, start, end)
                try:
                    if (len(path)) < bestFoodDistance:
                        bestFood = i
                        bestFoodDistance = len(path)
                        bestPath = path
                except TypeError:
                    path = "no path"

    
    if bestPath == "no path":
        return bestPath

    for j in range(len(bestPath)):
        tempRow = int((bestPath[j][0] - shift[0]) % numRows)
        tempCol = int((bestPath[j][1] - shift[1]) % numCols)
        bestPath[j] = (tempRow, tempCol)

    #food = observation.food[bestFood]
    #food_row, food_column = row_col(food, configuration.columns)

    #This will need to be changed, food distance depends on direction snake just traveled, whether other geese are close (as it could be pointless) and which spots on the board are filled
    #Will implement a map solving algorithm for all alive geese and if our goose has shortest distance, will select food that way.
    
    #Could also implement escape route algorithm? Don't know how that would work, ask ben

    return bestPath
            
def agent(obs_dict, config_dict):
    
    global which_turn
    which_turn += 1
    
    t0= time.clock()
    f = open("./myfile1.txt", "a")
    f.write("\n")
    f.write("Starting file" + "\n")
    
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    #player_goose is list of all bodypart positions
    player_head = player_goose[0]
    player_row, player_column = row_col(player_head, configuration.columns)
    start = (player_row, player_column)
    
    
    f.write("Commencing turn: " + str(which_turn))
    with open('./myfile2.txt', 'a') as testfile:
        testfile.write("Player_index: " + str(player_index) + " [0: White, 1: Blue, 2: Green, 3: Red], " + "\n")
    f.write("Player_index: " + str(player_index) + " [0: White, 1: Blue, 2: Green, 3: Red], " + "\n")
    """This agent always moves toward observation.food[0] but does not take advantage of board wrapping"""
    

    Matrix, MatrixNoFood, MatrixHeadAvoid1, MatrixHeadAvoid2 = fill_matrix(observation, configuration)
    
    f.write("Matrix filled" + "\n")
    
    
    
    
    
    [MatrixNoFood, MatrixHeadAvoid1, MatrixHeadAvoid2], start, shift = shift_matrix([MatrixNoFood, MatrixHeadAvoid1, MatrixHeadAvoid2], start)
    f.write("Matrix shifted" + "\n")
    f.write("Start coords " + str(start) + "\n")

    
    
    
    #MatrixToUse = MatrixNoFood
    #MatrixToUse = MatrixHeadAvoid2
    #MatrixToUse = MatrixHeadAvoid1
    #MatrixBackup1 = MatrixHeadAvoid1
    #MatrixBackup2 = MatrixNoFood
    
    #MatrixsToUse = [MatrixHeadAvoid2, MatrixHeadAvoid1, MatrixNoFood]
    
    MatrixsToUse = [MatrixHeadAvoid1, MatrixNoFood]
    
    
    #will replace player_row, player_column with 2d array that has all positions filled with all player information
    path = path_to_closest_food(observation, configuration, MatrixsToUse, start, shift)
    if path == "no path":
        player_index = observation.index
        player_goose = observation.geese[player_index]
        player_end = player_goose[len(player_goose)-1]
        player_end_row, player_end_column = row_col(player_end, configuration.columns)
        for MatrixToUse in MatrixsToUse:
            if path == "no path":
                if start == (player_end_row, player_end_column):
                    path = astar(MatrixToUse, start, (player_end_row+3, player_end_column+5))
                else:
                    path = astar(MatrixToUse, start, (player_end_row, player_end_column))
    f.write("Path: " + str(path) + "\n")
        
    whichMove =  which_direction(path)
    
    t1 = time.clock() - t0
    f.write("This is turn: " + str(int(which_turn)) + " , chosen movement: " )
    f.write(str(whichMove))
    f.write(" which took " + str(t1) + " seconds")
    f.close()
    return whichMove