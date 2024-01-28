import random
import dill
from game import Game, Move, Player
from strategies.minmax import wrap_min_max
from copy import deepcopy
from strategies.utils import CustomGame
from tqdm.auto import tqdm
class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move


class MyPlayer(Player):
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
        custom_game = CustomGame(game)
        ply = wrap_min_max(custom_game)
        
        if ply is None:
            ## Random play
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        else:
            from_pos = ply[0]
            move = ply[1]
        
        return from_pos, move


def test_min_max(args):


    player1 = MinMaxPlayer()
    player2 = RandomPlayer()



    if args.player==1:
        print('Testing with player 1... ')


        win = 0
        lose = 0
        draw = 0

        for i in tqdm(range(100)):
            #print(i)
            g = Game()
            winner = g.play(player1, player2)
            if winner == 0:
                win += 1
            elif winner == 1:
                lose += 1
            else:
                draw += 1
        print("your player win: ",win," times")
        print("your player lose: ",lose," times")
        print("your player draw: ",draw," times")
    elif args.player==2:
        print('Testing with player 2... ')

        win = 0
        lose = 0
        draw = 0

        for i in tqdm(range(100)):
            #print(i)
            g = Game()
            winner = g.play(player2, player1)
            if winner == 1:
                win += 1
            elif winner == 0:
                lose += 1
            else:
                draw += 1
        print("your player win: ",win," times")
        print("your player lose: ",lose," times")
        print("your player draw: ",draw," times")
    else:
        print('Testing with player 1... ')


        win = 0
        lose = 0
        draw = 0

        for i in tqdm(range(100)):
            #print(i)
            g = Game()
            winner = g.play(player1, player2)
            if winner == 0:
                win += 1
            elif winner == 1:
                lose += 1
            else:
                draw += 1
        print("your player win: ",win," times")
        print("your player lose: ",lose," times")
        print("your player draw: ",draw," times")


        print('Testing with player 2... ')

        win = 0
        lose = 0
        draw = 0

        for i in tqdm(range(100)):
            #print(i)
            g = Game()
            winner = g.play(player2, player1)
            if winner == 1:
                win += 1
            elif winner == 0:
                lose += 1
            else:
                draw += 1
        print("your player win: ",win," times")
        print("your player lose: ",lose," times")
        print("your player draw: ",draw," times")



        

