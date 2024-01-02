from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
import numpy as np
from collections import namedtuple
from strategies.rl import Boards_numpy
from tqdm import tqdm
# Rules on PDF


class Move(Enum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3


class Player(ABC):
    def __init__(self) -> None:
        '''You can change this for your player if you need to handle state/have memory'''
        pass

    @abstractmethod
    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        '''
        game: the Quixo game. You can use it to override the current game with yours, but everything is evaluated by the main game
        return values: this method shall return a tuple of X,Y positions and a move among TOP, BOTTOM, LEFT and RIGHT
        '''
        pass
def crea_stato_da_array(array):
    
    # Inizializza gli attributi dello stato
    State = namedtuple('State', ['x', 'o'])
    x_coordinates = []
    o_coordinates = []

    # Scansiona l'array e registra le coordinate
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            if array[i, j] == 1:
                x_coordinates.append((i, j))
            elif array[i, j] == 0:
                o_coordinates.append((i, j))

    # Crea un'istanza della namedtuple con le coordinate
    stato = State(x=x_coordinates, o=o_coordinates)
    return stato
def stampa_dizionario(dizionario, livello=0):
    spazi = "  " * livello
    for chiave, valore in dizionario.items():
        if isinstance(valore, dict):
            print(f"{spazi}{chiave}:")
            stampa_dizionario(valore, livello + 1)
        else:
            print(f"{spazi}{chiave}: {valore}")
class Game(object):
    def __init__(self) -> None:
        self._board = np.ones((5, 5), dtype=np.uint8) * -1
        self.current_player_idx = 1

    def get_board(self) -> np.ndarray:
        '''
        Returns the board
        '''
        return deepcopy(self._board)

    def get_current_player(self) -> int:
        '''
        Returns the current player
        '''
        return deepcopy(self.current_player_idx)
  
    def print(self):
        '''Prints the board. -1 are neutral pieces, 0 are pieces of player 0, 1 pieces of player 1'''
        print(self._board)

    def check_winner(self) -> int:
        '''Check the winner. Returns the player ID of the winner if any, otherwise returns -1'''
        # for each row
        for x in range(self._board.shape[0]):
            # if a player has completed an entire row
            if self._board[x, 0] != -1 and all(self._board[x, :] == self._board[x, 0]):
                # return the relative id
                return self._board[x, 0]
        # for each column
        for y in range(self._board.shape[1]):
            # if a player has completed an entire column
            if self._board[0, y] != -1 and all(self._board[:, y] == self._board[0, y]):
                # return the relative id
                return self._board[0, y]
        # if a player has completed the principal diagonal
        if self._board[0, 0] != -1 and all(
            [self._board[x, x]
                for x in range(self._board.shape[0])] == self._board[0, 0]
        ):
            # return the relative id
            return self._board[0, 0]
        # if a player has completed the secondary diagonal
        if self._board[0, -1] != -1 and all(
            [self._board[x, -(x + 1)]
             for x in range(self._board.shape[0])] == self._board[0, -1]
        ):
            # return the relative id
            return self._board[0, -1]
        return -1
    def train_rl(self,steps,learning_rate,discount_factor,player:Player):
        players = [player,player]
        winner = -1
        value_dictionary = {}
       
        for _ in tqdm(range(steps)):
            current_board=Boards_numpy()
            next_board=Boards_numpy()
            while winner<0:
                current_board=Boards_numpy()
                next_board=Boards_numpy()
                self.current_player_idx += 1
                self.current_player_idx %= len(players)
                ok=False
                while not ok:
                    from_pos,slide=players[self.current_player_idx].make_move(self)
                    current_board.current=crea_stato_da_array(self.get_board())
                    current_board.current=current_board.get_equivalent()
                    tmp=self.__move(from_pos,slide,self.current_player_idx)
                    next_board.current=crea_stato_da_array(self.get_board())
                    next_board.current=next_board.get_equivalent()
                    ok=tmp
                reward=self.check_winner()
                if reward==0:
                    reward=-1
                elif reward==-1:
                    reward=0
                action=str(from_pos)+" "+str(slide)
                if current_board not in value_dictionary:
                    value_dictionary[current_board]={action:0.}
                elif action not in value_dictionary[current_board]:
                    value_dictionary[current_board][action] = 0. 
                if next_board not in value_dictionary:
                    value_dictionary[next_board]={action:0.}
                elif action not in value_dictionary[next_board]:
                        value_dictionary[next_board][action] = 0. 
                if self.current_player_idx==0:
                    stampa_dizionario(value_dictionary)
                    print(current_board,action)
                    print("l'equivalente:",current_board.get_equivalent())
                    if current_board not in value_dictionary:
                       print("non trova la board")
                    elif action not in value_dictionary[current_board]:
                        print("non trova l'azione")

                    value_dictionary[current_board][action] = ((1 - learning_rate) * value_dictionary[current_board][action] + 
                            learning_rate * (reward + discount_factor * max(value_dictionary[next_board].values())))
                else:
                    stampa_dizionario(value_dictionary)
                    print(current_board,action)
                    print("l'equivalente:",current_board.get_equivalent())

                    if current_board not in value_dictionary:
                       print("non trova la board")
                    elif action not in value_dictionary[current_board]:
                        print("non trova l'azione")
                    value_dictionary[current_board][action] = ((1 - learning_rate) * value_dictionary[current_board][action] + 
                            learning_rate * (reward + discount_factor * min(value_dictionary[next_board].values())))
                
                winner=self.check_winner()
        stampa_dizionario(value_dictionary)


    def play(self, player1: Player, player2: Player) -> int:
        '''Play the game. Returns the winning player'''
        players = [player1, player2]
        winner = -1
        while winner < 0:
            self.current_player_idx += 1
            self.current_player_idx %= len(players)
            ok = False
            print(self._board)  
            while not ok:
                from_pos, slide = players[self.current_player_idx].make_move(
                    self)
                print(from_pos,slide)
                ok = self.__move(from_pos, slide, self.current_player_idx)
                
                """
                l'idea è di costruire un dizionario di stato azione 
                dove per lo stato lo trovo chiamando la funzione creao_stato_da_array in selfboard oppure rl.get_coordinates
                """
            print(self._board)  
            winner = self.check_winner()
        return winner

    def __move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        '''Perform a move'''
        if player_id > 2:
            return False
        # Oh God, Numpy arrays
        prev_value = deepcopy(self._board[(from_pos[1], from_pos[0])])
        acceptable = self.__take((from_pos[1], from_pos[0]), player_id)
        if acceptable:
            acceptable = self.__slide((from_pos[1], from_pos[0]), slide)
            if not acceptable:
                self._board[(from_pos[1], from_pos[0])] = deepcopy(prev_value)
        return acceptable

    def __take(self, from_pos: tuple[int, int], player_id: int) -> bool:
        '''Take piece'''
        # acceptable only if in border
        acceptable: bool = (
            # check if it is in the first row
            (from_pos[0] == 0 and from_pos[1] < 5)
            # check if it is in the last row
            or (from_pos[0] == 4 and from_pos[1] < 5)
            # check if it is in the first column
            or (from_pos[1] == 0 and from_pos[0] < 5)
            # check if it is in the last column
            or (from_pos[1] == 4 and from_pos[0] < 5)
            # and check if the piece can be moved by the current player
        ) and (self._board[from_pos] < 0 or self._board[from_pos] == player_id)
        if acceptable:
            self._board[from_pos] = player_id
        return acceptable

    def __slide(self, from_pos: tuple[int, int], slide: Move) -> bool:
        '''Slide the other pieces'''
        # define the corners
        SIDES = [(0, 0), (0, 4), (4, 0), (4, 4)]
        # if the piece position is not in a corner
        if from_pos not in SIDES:
            # if it is at the TOP, it can be moved down, left or right
            acceptable_top: bool = from_pos[0] == 0 and (
                slide == Move.BOTTOM or slide == Move.LEFT or slide == Move.RIGHT
            )
            # if it is at the BOTTOM, it can be moved up, left or right
            acceptable_bottom: bool = from_pos[0] == 4 and (
                slide == Move.TOP or slide == Move.LEFT or slide == Move.RIGHT
            )
            # if it is on the LEFT, it can be moved up, down or right
            acceptable_left: bool = from_pos[1] == 0 and (
                slide == Move.BOTTOM or slide == Move.TOP or slide == Move.RIGHT
            )
            # if it is on the RIGHT, it can be moved up, down or left
            acceptable_right: bool = from_pos[1] == 4 and (
                slide == Move.BOTTOM or slide == Move.TOP or slide == Move.LEFT
            )
        # if the piece position is in a corner
        else:
            # if it is in the upper left corner, it can be moved to the right and down
            acceptable_top: bool = from_pos == (0, 0) and (
                slide == Move.BOTTOM or slide == Move.RIGHT)
            # if it is in the lower left corner, it can be moved to the right and up
            acceptable_left: bool = from_pos == (4, 0) and (
                slide == Move.TOP or slide == Move.RIGHT)
            # if it is in the upper right corner, it can be moved to the left and down
            acceptable_right: bool = from_pos == (0, 4) and (
                slide == Move.BOTTOM or slide == Move.LEFT)
            # if it is in the lower right corner, it can be moved to the left and up
            acceptable_bottom: bool = from_pos == (4, 4) and (
                slide == Move.TOP or slide == Move.LEFT)
        # check if the move is acceptable
        acceptable: bool = acceptable_top or acceptable_bottom or acceptable_left or acceptable_right
        # if it is
        if acceptable:
            # take the piece
            piece = self._board[from_pos]
            # if the player wants to slide it to the left
            if slide == Move.LEFT:
                # for each column starting from the column of the piece and moving to the left
                for i in range(from_pos[1], 0, -1):
                    # copy the value contained in the same row and the previous column
                    self._board[(from_pos[0], i)] = self._board[(
                        from_pos[0], i - 1)]
                # move the piece to the left
                self._board[(from_pos[0], 0)] = piece
            # if the player wants to slide it to the right
            elif slide == Move.RIGHT:
                # for each column starting from the column of the piece and moving to the right
                for i in range(from_pos[1], self._board.shape[1] - 1, 1):
                    # copy the value contained in the same row and the following column
                    self._board[(from_pos[0], i)] = self._board[(
                        from_pos[0], i + 1)]
                # move the piece to the right
                self._board[(from_pos[0], self._board.shape[1] - 1)] = piece
            # if the player wants to slide it upward
            elif slide == Move.TOP:
                # for each row starting from the row of the piece and going upward
                for i in range(from_pos[0], 0, -1):
                    # copy the value contained in the same column and the previous row
                    self._board[(i, from_pos[1])] = self._board[(
                        i - 1, from_pos[1])]
                # move the piece up
                self._board[(0, from_pos[1])] = piece
            # if the player wants to slide it downward
            elif slide == Move.BOTTOM:
                # for each row starting from the row of the piece and going downward
                for i in range(from_pos[0], self._board.shape[0] - 1, 1):
                    # copy the value contained in the same column and the following row
                    self._board[(i, from_pos[1])] = self._board[(
                        i + 1, from_pos[1])]
                # move the piece down
                self._board[(self._board.shape[0] - 1, from_pos[1])] = piece
        return acceptable
