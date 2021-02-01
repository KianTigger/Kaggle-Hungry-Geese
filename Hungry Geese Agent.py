from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col

#11 columns of 7 rows, can move from 1st column to 11th column and 1st row to 7th row.
#Minimum of 2 food units on board at all times.
#Every 40 steps goose loses segment.
#The reward is calculated as the current turn + goose length.
#Surviving agents at the end of the episode receive maximum reward as (2 * episode steps) + length.
#200 steps each turn.
#Surviving agents receive maximum reward 2∗configuration.episodeSteps.

#Don't know who survives in head on collisions?


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

