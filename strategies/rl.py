from itertools import combinations
from collections import namedtuple
from random import choice
from copy import deepcopy
import functools
import numpy as np
from tqdm.auto import tqdm
class CustomState(namedtuple('State', ['x', 'o'])):
    #for the hash we generate all possible configuration from one state and then we re order the vector with comapre fucntion and extract first element
    #in this way we have always the same configuration

    def __eq__(self, other_state):
        #To see if one representation is equivalent to another one we extract indices in the 'MAGIC' board 
        #and then we search those indexes in all magic boards to extract the equivalent representations
        #If one is equivalent to other_state, the two state are the same

        state_indexes = find_indexes(self)
        for magic in MAGIC_BOARDS:
            representation = get_representation_by_index(state_indexes, magic)
            if (sorted(representation.x) == sorted(other_state.x) and sorted(representation.o) == sorted(other_state.o)):
                return True
            
        return False

    def __hash__(self):
        #We generate all possible equivalent representations from one state
        #and then we re-order them with 'compare' function, we extract first element 
        #and then we apply hash functio to its string representation

        rappresentations = get_equivalent_representations(self)
        sorted_rappresentations = sorted(rappresentations, key=functools.cmp_to_key(compare))

        return hash(str(sorted_rappresentations))
    
    def unique_representation(self):
        #This function convert the state in its unique representation         
        rappresentations = get_equivalent_representations(self)
        sorted_rappresentations = sorted(rappresentations, key=functools.cmp_to_key(compare))
            
        return CustomState(sorted_rappresentations[0].x, sorted_rappresentations[0].o)
def check_winner(board) -> int:
        '''Check the winner. Returns the player ID of the winner if any, otherwise returns -1'''
        # for each row
        for x in range(board.shape[0]):
            # if a player has completed an entire row
            if board[x, 0] != -1 and all(board[x, :] == board[x, 0]):
                # return the relative id
                return board[x, 0]
        # for each column
        for y in range(board.shape[1]):
            # if a player has completed an entire column
            if board[0, y] != -1 and all(board[:, y] == board[0, y]):
                # return the relative id
                return board[0, y]
        # if a player has completed the principal diagonal
        if board[0, 0] != -1 and all(
            [board[x, x]
                for x in range(board.shape[0])] == board[0, 0]
        ):
            # return the relative id
            return board[0, 0]
        # if a player has completed the secondary diagonal
        if board[0, -1] != -1 and all(
            [board[x, -(x + 1)]
             for x in range(board.shape[0])] == board[0, -1]
        ):
            # return the relative id
            return board[0, -1]
        return -1
class Boards():
    def __init__(self):
        self.board=list(range(1, 26))
        self.board_90=[21,16,11,6,1,22,17,12,7,2,23,18,13,8,3,24,19,14,9,4,25,20,15,10,5]
        self.board_180=list(range(25, 0, -1))
        self.board_270=[5,10,15,20,25,4,9,14,19,24,3,8,13,18,23,2,7,12,17,22,1,6,11,16,21]
        self.mirror_board=[21,22,23,24,25,16,17,18,19,20,11,12,13,14,15,6,7,8,9,10,1,2,3,4,5]
        self.mirror_board_90=[25,20,15,10,5,24,19,14,9,4,23,18,13,8,3,22,17,12,7,2,21,16,11,6,1]
        self.mirror_board_180=[5,4,3,2,1,10,9,8,7,6,15,14,13,12,11,20,19,18,17,16,25,24,23,22,21]
        self.mirror_board_270=[1,6,11,16,21,2,7,12,17,22,3,8,13,18,23,4,9,14,19,24,5,10,15,20,25]
        self.state= namedtuple('State', ['x', 'o'])    

State = namedtuple('state', ['x', 'o'])

def get_coordinates(matrix):
    x_coordinates = set()
    o_coordinates = set()

    rows, cols = np.shape(matrix)

    for i in range(rows):
        for j in range(cols):
            if matrix[i, j] == 0:
                x_coordinates.add((i, j))
            elif matrix[i, j] == 1:
                o_coordinates.add((i, j))

    return State(x=x_coordinates, o=o_coordinates)        
class Boards_numpy():
    def __init__(self):
        State=namedtuple('state',['x','o'])
        self.current=State(x=set(),o=set())
        self.state=np.full((5, 5), -1)
        self.board=np.array(list(range(1, 26))).reshape(5,5)
        self.board_90=np.array([21,16,11,6,1,22,17,12,7,2,23,18,13,8,3,24,19,14,9,4,25,20,15,10,5]).reshape(5,5)
        self.board_180=np.array(list(range(25, 0, -1))).reshape(5,5)
        self.board_270=np.array([5,10,15,20,25,4,9,14,19,24,3,8,13,18,23,2,7,12,17,22,1,6,11,16,21]).reshape(5,5)
        self.mirror_board=np.array([21,22,23,24,25,16,17,18,19,20,11,12,13,14,15,6,7,8,9,10,1,2,3,4,5]).reshape(5,5)
        self.mirror_board_90=np.array([25,20,15,10,5,24,19,14,9,4,23,18,13,8,3,22,17,12,7,2,21,16,11,6,1]).reshape(5,5)
        self.mirror_board_180=np.array([5,4,3,2,1,10,9,8,7,6,15,14,13,12,11,20,19,18,17,16,25,24,23,22,21]).reshape(5,5)
        self.mirror_board_270=np.array([1,6,11,16,21,2,7,12,17,22,3,8,13,18,23,4,9,14,19,24,5,10,15,20,25]).reshape(5,5)
        self.all=[self.board,self.board_90,self.board_180,self.board_270,self.mirror_board,self.mirror_board_90,self.mirror_board_180,self.board_270]
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
        return str(self.current)

    def q_learning(steps, learning_rate, discount_factor):
        value_dictionary = {}

        for _ in tqdm(range(steps)):
            current_state = CustomState(set(), set())
            cnt = 0
            
            while current_state.x.union(current_state.o) != set(range(1, 26)) and check_winner(current_state) == -1:
                next_state = deepcopy(current_state)
                current_state = current_state.unique_representation()
                next_state = next_state.unique_representation()
                action = random_move(set(range(1, 10)) - (current_state.x.union(current_state.o)))
                player = cnt % 2
                cnt += 1

                if player == 1:
                    next_state.x.add(action)
                    next_state = next_state.unique_representation()
                    reward = state_value(next_state)

                    if(reward == 0):
                        if block_win_adv(next_state.o, action):
                            reward = 0.75
                        elif trap_condition(next_state.x, next_state.o):
                            reward = 0.5

                    if current_state not in value_dictionary:
                        value_dictionary[current_state] = {action: 0.}
                    elif action not in value_dictionary[current_state]:
                        value_dictionary[current_state][action] = 0.

                    if next_state not in value_dictionary:
                        value_dictionary[next_state] = {action: 0.}
                    elif action not in value_dictionary[next_state]:
                        value_dictionary[next_state][action] = 0.

                    value_dictionary[current_state][action] = ((1 - learning_rate) * value_dictionary[current_state][action] + 
                        learning_rate * (reward + discount_factor * max(value_dictionary[next_state].values())))
                    current_state = deepcopy(next_state)

                else:  
                    next_state.o.add(action)
                    next_state = next_state.unique_representation()
                    reward = state_value(next_state)

                    if(reward == 0):
                        if block_win_adv(next_state.x, action):
                            reward = -0.75
                        elif trap_condition(next_state.o, next_state.x):
                            reward = -0.5

                    if current_state not in value_dictionary:
                        value_dictionary[current_state] = {action: 0.}
                    elif action not in value_dictionary[current_state]:
                        value_dictionary[current_state][action] = 0.

                    if next_state not in value_dictionary:
                        value_dictionary[next_state] = {action: 0.}
                    elif action not in value_dictionary[next_state]:
                        value_dictionary[next_state][action] = 0.

                    value_dictionary[current_state][action] = ((1 - learning_rate) * value_dictionary[current_state][action] + 
                        learning_rate * (reward + discount_factor * min(value_dictionary[next_state].values())))
                    current_state = deepcopy(next_state)

        return value_dictionary       

    def get_equivalent(self):
        _tmp = namedtuple('state', ['x', 'o'])
        State = namedtuple('state', ['x', 'o'])
        elenco_ordinato=[]
        for matrix in self.all:
            tmp_x=ottieni_valori_da_coordinate(matrix,self.current.x)
            tmp_x=trova_coordinate_per_valori(self.board,tmp_x)
            tmp_o=ottieni_valori_da_coordinate(matrix,self.current.o)
            tmp_o=trova_coordinate_per_valori(self.board,tmp_o)

            elenco_ordinato.append(deepcopy(State(x=tmp_x,o=tmp_o)))
        
        
        elenco_ordinato = sorted(elenco_ordinato, key=lambda state: (sorted(state.x), sorted(state.o)))
        #print("\n",elenco_ordinato)

        # Crea nuove namedtuple con le tuple ordinate
        elenco_ordinato = [State(x=sorted(state.x), o=sorted(state.o)) for state in elenco_ordinato]#riordino le tuple anche
        #print("\n",elenco_ordinato)
        return elenco_ordinato[0]
    

    
def trova_coordinate_per_valori(array, insieme_di_valori):
        coordinate = [(i, j) for i, row in enumerate(array) for j, val in enumerate(row) if val in insieme_di_valori]
        return coordinate
def ottieni_valori_da_coordinate(array, insieme_di_coordinate):
        valori = [array[coord] for coord in insieme_di_coordinate]
        return valori
def q_learning(steps, learning_rate, discount_factor):
    value_dictionary = {}

    for _ in tqdm(range(steps)):
        current_state = CustomState(set(), set())
        cnt = 0
        
        while current_state.x.union(current_state.o) != set(range(1, 26)) and check_winner(current_state) == -1:
            next_state = deepcopy(current_state)
            current_state = current_state.unique_representation()
            next_state = next_state.unique_representation()
            action = random_move(set(range(1, 10)) - (current_state.x.union(current_state.o)))
            player = cnt % 2
            cnt += 1

            if player == 1:
                next_state.x.add(action)
                next_state = next_state.unique_representation()
                reward = state_value(next_state)

                if(reward == 0):
                    if block_win_adv(next_state.o, action):
                        reward = 0.75
                    elif trap_condition(next_state.x, next_state.o):
                        reward = 0.5

                if current_state not in value_dictionary:
                    value_dictionary[current_state] = {action: 0.}
                elif action not in value_dictionary[current_state]:
                    value_dictionary[current_state][action] = 0.

                if next_state not in value_dictionary:
                    value_dictionary[next_state] = {action: 0.}
                elif action not in value_dictionary[next_state]:
                    value_dictionary[next_state][action] = 0.

                value_dictionary[current_state][action] = ((1 - learning_rate) * value_dictionary[current_state][action] + 
                    learning_rate * (reward + discount_factor * max(value_dictionary[next_state].values())))
                current_state = deepcopy(next_state)

            else:  
                next_state.o.add(action)
                next_state = next_state.unique_representation()
                reward = state_value(next_state)

                if(reward == 0):
                    if block_win_adv(next_state.x, action):
                        reward = -0.75
                    elif trap_condition(next_state.o, next_state.x):
                        reward = -0.5

                if current_state not in value_dictionary:
                    value_dictionary[current_state] = {action: 0.}
                elif action not in value_dictionary[current_state]:
                    value_dictionary[current_state][action] = 0.

                if next_state not in value_dictionary:
                    value_dictionary[next_state] = {action: 0.}
                elif action not in value_dictionary[next_state]:
                    value_dictionary[next_state][action] = 0.

                value_dictionary[current_state][action] = ((1 - learning_rate) * value_dictionary[current_state][action] + 
                    learning_rate * (reward + discount_factor * min(value_dictionary[next_state].values())))
                current_state = deepcopy(next_state)

    return value_dictionary       





        
