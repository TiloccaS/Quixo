from game import Game, Player, Move

import random
from itertools import product
from copy import deepcopy
from strategies.minmax import wrap_min_max
class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move
    
class MinMaxPlayer(Player):
    def __init__(self) -> None:
        super().__init__()
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        ply = wrap_min_max(game,game.current_player_idx)
        
        if ply[0] is None:
            ## Random play
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        else:
            from_pos = ply[0]
            move = ply[1]
        
        return from_pos, move

class CustomGame(Game):
    def __init__(self) -> None:
        super().__init__()

    def move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        return super()._Game__move(from_pos, slide, player_id)
    def getPossibleMoves(self,player_id:int):
        possible_moves=[]
        first_two_numbers = range(5)
        last_number = range(4)
        all_combinations = list(product(first_two_numbers, first_two_numbers, last_number))
        for a in all_combinations:
            tmp=deepcopy(self)
            if tmp.move((a[0],a[1]),Move(a[2]),player_id)==True:
                possible_moves.append(((a[0],a[1]),Move(a[2])))
        random.shuffle(possible_moves)
        return possible_moves