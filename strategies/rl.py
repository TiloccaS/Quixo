from itertools import combinations
from collections import namedtuple
from random import choice
from copy import deepcopy
import functools
import numpy as np
from tqdm.auto import tqdm

State = namedtuple('state', ['x', 'o'])

def get_coordinates(matrix):
    x_coordinates = set()
    o_coordinates = set()
    #restituisce le coordinate dove in x mette gli elementi con 0 e in o le coordinate con 1
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
        self.current=State(x=set(),o=set())#stato attuale del gioco
        #board
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

    def get_equivalent(self):
        _tmp = namedtuple('state', ['x', 'o'])
        State = namedtuple('state', ['x', 'o'])
        elenco_ordinato=[]
        """
        funziona cosi:
        -li passo le coordinate 
        -trova i valori per la matrice i per le coordinate che li ho passato
        -da i valori ottenuti dalla matrice i ottengo le coordinate sulla board principale
        -questa è una possibile configurazione
        """
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


        
