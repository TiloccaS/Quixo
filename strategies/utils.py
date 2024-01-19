from game import Game, Player, Move

import random

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move
    

class CustomGame(Game):
    def __init__(self) -> None:
        super().__init__()

    def move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        return super()._Game__move(from_pos, slide, player_id)