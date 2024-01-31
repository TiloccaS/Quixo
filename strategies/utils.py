import random
from game import Game, Player, Move
from itertools import product
from tqdm.auto import tqdm
from copy import deepcopy

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move
    
class CustomGame(Game):
    def __init__(self, game=None) -> None:
        super().__init__()
        if game is not None:
            self._board = game.get_board()
            self.current_player_idx = game.get_current_player()

    def move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        return super()._Game__move(from_pos, slide, player_id)
    
    def getPossibleMoves(self, player_id):
        possible_moves = []
        first_two_numbers = range(5)
        last_number = range(4)
        all_combinations = list(product(first_two_numbers, first_two_numbers, last_number))

        for c in all_combinations:
            tmp = deepcopy(self)
            if tmp.move((c[0], c[1]), Move(c[2]), player_id) == True:
                possible_moves.append(((c[0], c[1]), Move(c[2])))

        random.shuffle(possible_moves)
        return possible_moves
    
    def modify_board(self, board):
        self._board = board

def test(player1, player2, num_games):
    win = 0
    lose = 0
    draw = 0

    for _ in tqdm(range(num_games)):
        g = Game()
        winner = g.play(player1, player2)

        if winner == 0:
            win += 1
        elif winner == 1:
            lose += 1
        else:
            draw += 1

    return win, lose, draw
    