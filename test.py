import random
import dill
from game import Game, Move, Player
from tqdm.auto import tqdm
from strategies.rl import Q_learing, CustomState,  get_coordinates

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
    
class RLPlayer(Player):
    def __init__(self, learning_rate=0.1, discount_factor=0.7, pretrain_path=None, save_model_path=None, max_steps=None, train=False) -> None:
        super().__init__()
        if train:
            ql = Q_learing(learning_rate, discount_factor, pretrain_path=pretrain_path, max_steps=max_steps)
            steps, self.value_dictionary = ql.train()

            if save_model_path is not None:
                d = {'steps': steps, 'value_dictionary': self.value_dictionary}

                with open(save_model_path, 'wb') as outfile:
                    dill.dump(d, outfile)
        elif not train and pretrain_path is not None:
            with open(pretrain_path, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary = d['value_dictionary']
            print(len(self.value_dictionary))
        
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        current_state = CustomState(get_coordinates(game.get_board()))

        if current_state in self.value_dictionary:
            list_action = sorted(self.value_dictionary[current_state], key=self.value_dictionary[current_state].get)

            action = list_action[0].split('-')
            from_pos = tuple((int(c) for c in action[0] if c.isdigit()))

            if action[1] == 'Move.LEFT':
                move = Move.LEFT
            elif action[1] == 'Move.RIGHT':
                move = Move.RIGHT
            elif action[1] == 'Move.TOP':
                move = Move.TOP
            else:
                move = Move.BOTTOM
        else:
            ## Random play
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
            
        return from_pos, move
    
player1 = RLPlayer(pretrain_path='train_results/rl.pik')
player2 = RandomPlayer()


win = 0
lose = 0
draw = 0
for _ in tqdm(range(5)):
    g = Game()
    winner = g.play(player1, player2)
    if winner == 0:
        win += 1
    elif winner == 1:
        lose += 1
    else:
        draw += 1

print(win)
print(lose)
print(draw)