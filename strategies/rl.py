from game import Game, Move, Player
from collections import namedtuple
from copy import deepcopy

import random
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

def get_coordinates_from_board_positions(board, positions):#trova_coordinate_per_valori(array, insieme_di_valori):
        #coordinates = [(j, i) for i, row in enumerate(board) for j, val in enumerate(row) if val in positions]
        cnt = 0
        coordinates = []
        rows, cols = np.shape(board)
        for i in range(rows):
            for j in range(cols):
                if board[i, j] in positions:
                    coordinates.append((j, i))
                    cnt += 1
                    if cnt == len(positions):    ### stop condition per migliorare prestazioni
                        return coordinates
        return coordinates

def get_board_positions_from_coordinates(board, coordinates):#ottieni_valori_da_coordinate(array, insieme_di_coordinate):
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
        #self.board = np.full((5, 5), -1)    

    def __eq__(self, other_state):
        #To see if one representation is equivalent to another one we extract indices in the 'MAGIC' board 
        #and then we search those indexes in all magic boards to extract the equivalent representations
        #If one is equivalent to other_state, the two state are the same

        a=self.get_equivalent()
        b=other_state.get_equivalent()

        return (a.x==b.x and a.o==b.o)
    def __hash__(self):
        a=self.get_equivalent()
        #print("my a is this:", a)
        return hash(str(a))
    def __str__(self):
        return str(self.state)

    def get_equivalent(self):    ##### Controllare
        elenco_ordinato=[]
        """
        funziona cosi:
        -li passo le coordinate 
        -trova i valori per la matrice i per le coordinate che li ho passato
        -da i valori ottenuti dalla matrice i ottengo le coordinate sulla board principale
        -questa è una possibile configurazione
        """
        for board in Board.ALL:
            tmp_x = get_board_positions_from_coordinates(board, self.state.x)
            tmp_x = get_coordinates_from_board_positions(Board.BOARD, tmp_x)
            tmp_o = get_board_positions_from_coordinates(board, self.state.o)
            tmp_o = get_coordinates_from_board_positions(Board.BOARD,tmp_o)

            elenco_ordinato.append(deepcopy(State(x = tmp_x, o = tmp_o)))
        
        elenco_ordinato = sorted(elenco_ordinato, key=lambda state: (sorted(state.x), sorted(state.o)))

        # Crea nuove namedtuple con le tuple ordinate
        elenco_ordinato = [State(x = sorted(state.x), o = sorted(state.o)) for state in elenco_ordinato]#riordino le tuple anche
        return elenco_ordinato[0]
    

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move


def print_dictionary(dictionary, level=0):
        spaces = "  " * level
        for key, value in dictionary.items():
            if isinstance(value, dict):
                print(f"{spaces}{key}:")
                print_dictionary(value, level + 1)
            else:
                print(f"{spaces}{key}: {value}")


class Q_learing():
    def __init__(self, steps, learning_rate, discount_factor):
        self.value_dictionary = {}
        self.steps = steps
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def train(self):
        players = [RandomPlayer(), RandomPlayer()]
        game = Game()

        for _ in tqdm(range(self.steps)):
            winner = -1
            current_state = CustomState()
            next_state = CustomState()

            while winner < 0:
                game.current_player_idx += 1
                game.current_player_idx %= len(players)
                current_state = CustomState()
                next_state = CustomState()

                ok = False

                while not ok:
                    '''from_pos, slide = players[game.get_current_player()].make_move(game)
                    current_state.state = get_coordinates(game.get_board())
                    current_state.state = current_state.get_equivalent()
                    ok = game.move(from_pos, slide, game.get_current_player())
                    print(ok)
                    next_state.state = get_coordinates(game.get_board())
                    next_state.state = next_state.get_equivalent()'''

                    from_pos,slide=players[game.current_player_idx].make_move(game)
                    current_state.state=get_coordinates(game.get_board())
                    current_state.state=current_state.get_equivalent()
                    tmp=game.move(from_pos,slide,game.current_player_idx)
                    next_state.state=get_coordinates(game.get_board())
                    next_state.state=next_state.get_equivalent()
                    ok=tmp

                reward = game.check_winner()
                if reward == 0:
                    reward = 1
                elif reward == 1:
                    reward = -1
                else:       
                    reward = 0

                action = str(from_pos) + " " + str(slide)

                if current_state not in self.value_dictionary:
                    self.value_dictionary[current_state]={action:0.}
                elif action not in self.value_dictionary[current_state]:            ## USIAMO DEFAULTDICT
                    self.value_dictionary[current_state][action] = 0. 

                if next_state not in self.value_dictionary:
                    self.value_dictionary[next_state]={action:0.}
                elif action not in self.value_dictionary[next_state]:
                        self.value_dictionary[next_state][action] = 0. 

                if game.get_current_player() == 0:
                    self.value_dictionary[current_state][action] = ((1 - self.learning_rate) * self.value_dictionary[current_state][action] + 
                            self.learning_rate * (reward + self.discount_factor * max(self.value_dictionary[next_state].values())))
                else:
                    self.value_dictionary[current_state][action] = ((1 - self.learning_rate) * self.value_dictionary[current_state][action] + 
                            self.learning_rate * (reward + self.discount_factor * min(self.value_dictionary[next_state].values())))
                winner=game.check_winner()
        print_dictionary(self.value_dictionary)
        return self.value_dictionary
    



        
