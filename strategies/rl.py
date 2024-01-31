from strategies.utils import RandomPlayer, CustomGame
from collections import namedtuple, defaultdict
from copy import deepcopy

import dill
import numpy as np
from tqdm.auto import tqdm

State = namedtuple('state', ['x', 'o'])

def get_coordinates(board):
    ## Returns current state, which contains 2 sets (1 for player) containing coordinates of player's positions
    x_coordinates = set()
    o_coordinates = set()
    rows, cols = np.shape(board)

    for i in range(rows):
        for j in range(cols):
            if board[i, j] == 0:
                x_coordinates.add((j, i))    
            elif board[i, j] == 1:
                o_coordinates.add((j, i))

    return State(x = x_coordinates, o = o_coordinates)

def get_coordinates_from_board_positions(board, positions):
        cnt = 0
        coordinates = []
        rows, cols = np.shape(board)
        for i in range(rows):
            for j in range(cols):
                if board[i, j] in positions:
                    coordinates.append((j, i))
                    cnt += 1
                    if cnt == len(positions):   
                        return coordinates
        return coordinates

def get_board_positions_from_coordinates(board, coordinates):
        positions = [board[y, x] for x, y in coordinates]
        return positions
      
class Board():
    BOARD = np.array(list(range(1, 26))).reshape(5,5)
    BOARD_90 = np.rot90(BOARD, 1)
    BOARD_180 = np.rot90(BOARD, 2)
    BOARD_270 = np.rot90(BOARD, 3)
    MIRROR_BOARD = np.flip(BOARD, axis=0)
    MIRROR_BOARD_90 = np.flip(BOARD_90, axis=0)
    MIRROR_BOARD_180 = np.flip(BOARD_180, axis=0)
    MIRROR_BOARD_270 = np.flip(BOARD_270, axis=0)
    ALL = [BOARD, BOARD_90, BOARD_180, BOARD_270, MIRROR_BOARD, MIRROR_BOARD_90, MIRROR_BOARD_180, MIRROR_BOARD_270]

class CustomState():
    def __init__(self, state=None):
        if state == None:
            self.state = State(x = set(), o = set())
        else:
            self.state = state         

    def __eq__(self, other_state):
        #To see if one representation is equivalent to another one we extract indices in the 'MAGIC' board 
        #and then we search those indexes in all magic boards to extract the equivalent representations
        #If one is equivalent to other_state, the two state are the same
    
        current_state = self.get_equivalent()
        other_state = other_state.get_equivalent()
        return current_state.x == other_state.x and current_state.o == other_state.o
    
    def __hash__(self):
        return hash(str(self.get_equivalent()))
    
    def __str__(self):
        return str(self.state)

    def get_equivalent(self):
        ordered_list=[]
        #To use equivalent represention we use board 5x5 where each cell is a number
        #1. We extract the cell's number from each board giving the coordinates
        #2. Then we extract the coordinates of those numbers in the principle board
        #3. We sort them and we extract the first 

        for board in Board.ALL:
            tmp_x = get_board_positions_from_coordinates(board, self.state.x)
            tmp_x = get_coordinates_from_board_positions(Board.BOARD, tmp_x)
            tmp_o = get_board_positions_from_coordinates(board, self.state.o)
            tmp_o = get_coordinates_from_board_positions(Board.BOARD,tmp_o)

            ordered_list.append(deepcopy(State(x = tmp_x, o = tmp_o)))
       
        ordered_list = sorted(ordered_list, key=lambda state: (sorted(state.x), sorted(state.o)))
       
        ordered_list = [State(x = sorted(state.x), o = sorted(state.o)) for state in ordered_list]
       
        return ordered_list[0]

def print_dictionary(dictionary, level=0, str=""):
        spaces = "  " * level
        for key, value in dictionary.items():
            if isinstance(value, dict):
                print(f"{spaces}{key}:")
                print_dictionary(value, level + 1)
            else:
                print(f"{spaces}{key}: {value}")

def build_board_from_coordinates(coordinates):
    board = np.full((5, 5), -1)  ## This is the empty board

    for x, y in coordinates.x:
        board[y, x] = 0  ## Adding 0 if (x, y) is a positions occupied by x

    for x, y in coordinates.o:
        board[y, x] = 1  # Adding 1 if (x, y) is a positions occupied by o

    return board

class Q_learing():
    ## we use 2 dictionary beacause a move of x could be not avaliable for o

    def __init__(self, learning_rate, discount_factor, pretrain_path_x=None, pretrain_path_o=None, max_steps=None):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.max_steps = max_steps
     
        if pretrain_path_x is None:
            self.value_dictionary_x = defaultdict(lambda: defaultdict(float))
            self.tot_steps = 0
        else:
            print('Reading dictionary of x...')
            ## we use dill beacause in this way we can save the class CustomState
            with open(pretrain_path_x, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary_x = d['value_dictionary']
            self.tot_steps = d['steps']

        if pretrain_path_o is None:
            self.value_dictionary_o = defaultdict(lambda: defaultdict(float))
            self.tot_steps = 0
        else:
            print('Reading dictionary of o...')
            with open(pretrain_path_o, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary_o = d['value_dictionary']
            self.tot_steps += d['steps']
        
    def train(self):
        cnt = 0
        steps = 0
        players = [RandomPlayer(), RandomPlayer()]

        def generator():
            while True:
                yield

        for _ in tqdm(generator()):
            steps += 1
            winner = -1
            dict_lenght_x = len(self.value_dictionary_x)
            dict_lenght_o = len(self.value_dictionary_o)

            game = CustomGame()

            while winner < 0:
                game.current_player_idx += 1
                game.current_player_idx %= len(players)
                current_state = CustomState()
                current_state.state = get_coordinates(game.get_board())
                current_state.state = current_state.get_equivalent()
                board_equivalent = build_board_from_coordinates(current_state.state)
                game.modify_board(board_equivalent)
                next_state = CustomState()
                next_state.state = deepcopy(current_state)

                ok = False

                while not ok:
                    from_pos, slide = players[game.get_current_player()].make_move(game)
                    ok = game.move(from_pos, slide, game.get_current_player())
                    if ok:
                        next_state.state = get_coordinates(game.get_board())
                        next_state.state = next_state.get_equivalent()
                       
                winner = game.check_winner()
                if winner == 0:
                    reward = 1
                elif winner == 1:
                    reward = -1
                else:       
                    reward = 0

                action = str(from_pos) + "-" + str(slide)
                
                if game.get_current_player() == 0:
                    if not self.value_dictionary_x[next_state]:
                        values = [0]
                    else:
                        values = self.value_dictionary_x[next_state].values()
                else:
                    if not self.value_dictionary_o[next_state]:
                        values = [0]
                    else:
                        values = self.value_dictionary_o[next_state].values()
                        
                if game.get_current_player() == 0:
                    self.value_dictionary_x[current_state][action] = ((1 - self.learning_rate) * self.value_dictionary_x[current_state][action] + 
                            self.learning_rate * (reward + self.discount_factor * max(values)))
                else:
                    self.value_dictionary_o[current_state][action] = ((1 - self.learning_rate) * self.value_dictionary_o[current_state][action] + 
                            self.learning_rate * (reward + self.discount_factor * min(values)))

            if  (len(self.value_dictionary_x) <= dict_lenght_x) and (len(self.value_dictionary_o) <= dict_lenght_o):
                cnt += 1
                if cnt == 100:
                    ## Early stop
                    ## If both dictionaries not increase length for 100 consecutive steps
                    ## It means that they reached convergence so training can finish
                    break
            else:
                cnt = 0

            if self.max_steps is not None:
                ## max_steps is a parameter that we can pass to decide
                ## the exact number of epoch we want to train
                if steps == self.max_steps:
                    break

        return self.tot_steps + steps, self.value_dictionary_x, self.value_dictionary_o
    



        
