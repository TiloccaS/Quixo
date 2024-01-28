import random
from game import Game, Move, Player
import random
import dill
from game import Game, Move, Player
from strategies.minmax import wrap_min_max
from copy import deepcopy
from strategies.utils import CustomGame
from tqdm.auto import tqdm
from strategies.rl import Q_learing, CustomState,  get_coordinates, build_board_from_coordinates,print_dictionary
import argparse
from test_min_max import test_min_max
from test_rl import test_rl
class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move

## MUST BE RL player
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

class RLPlayer(Player):
    def __init__(self, learning_rate=0.1, discount_factor=0.7, pretrain_path_x=None,pretrain_path_o=None, save_model_path_x=None,save_model_path_o=None, max_steps=None, train=False) -> None:
        super().__init__()
        self.cnt=0
        self.tot=0
        if train:
            ql = Q_learing(learning_rate, discount_factor, pretrain_path_x=pretrain_path_x,pretrain_path_o=pretrain_path_x, max_steps=max_steps)
            steps, self.value_dictionary_x,self.value_dictionary_o = ql.train()
            if save_model_path_x is not None:
                print('Saving dictionary of x...')
                print("length of dictionary of x: ",len(self.value_dictionary_x))
                d = {'steps': steps/2, 'value_dictionary': self.value_dictionary_x}

                with open(save_model_path_x, 'wb') as outfile_x:
                    dill.dump(d, outfile_x)

            if save_model_path_o is not None:
                print('Saving dictionary of o...')
                print("length of dictionary of o: ",len(self.value_dictionary_o))
                d = {'steps': steps/2, 'value_dictionary': self.value_dictionary_o}

                with open(save_model_path_o, 'wb') as outfile_o:
                    dill.dump(d, outfile_o)

        elif not train and pretrain_path_x is not None and pretrain_path_o is not None:
            print('Reading dictionary of x...')
            with open(pretrain_path_x, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary_x = d['value_dictionary']
            print("length of dictionary of x: ",len(self.value_dictionary_x))

            print('Reading dictionary of o...')
            with open(pretrain_path_o, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary_o = d['value_dictionary']
            print("length of dictionary of o: ",len(self.value_dictionary_o))
        
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        self.tot+=1
        game_tmp=CustomGame(game)
        current_state = CustomState(get_coordinates(game_tmp.get_board()))
        current_state.state=current_state.get_equivalent()
        #we use the equivalent represention for extract the equivalnt move
        game_tmp.modify_board(build_board_from_coordinates(deepcopy(current_state.state)))
        if game.get_current_player()==0:
                value_dictionary=self.value_dictionary_x

        else:
                value_dictionary=self.value_dictionary_o
        if current_state in value_dictionary:
            
            if game.get_current_player()==0:
                list_action = sorted(value_dictionary[current_state], key=value_dictionary[current_state].get,reverse=True)

            else:
                list_action = sorted(value_dictionary[current_state], key=value_dictionary[current_state].get)


            if len(list_action)>0:
                action = list_action[0].split('-')
                from_pos =tuple( (int(c) for c in action[0] if c.isdigit()))

                if action[1] == 'Move.LEFT':
                    move = Move.LEFT
                elif action[1] == 'Move.RIGHT':
                    move = Move.RIGHT
                elif action[1] == 'Move.TOP':
                    move = Move.TOP
                else:
                    move = Move.BOTTOM
                game._board=game_tmp._board
           
            else:
                 from_pos = (random.randint(0, 4), random.randint(0, 4))
                 move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])

        else:
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
            self.cnt+=1
        return from_pos, move

parser = argparse.ArgumentParser(description='Descrizione del tuo script.')
parser.add_argument('--strategy',type=int,help='strategy 0: both, strategy1: minmax, strategy 2: rl',default=0)
parser.add_argument('--pretrain_path_o',type=str, help='pretrain path of dictionary o', default='./train_results/rl_o.pik')
parser.add_argument('--pretrain_path_x', type=str, help='pretrain path of dictionary x',default='./train_results/rl_x.pik')
parser.add_argument('--save_model_path_x',type=str, help='path where you want save the dictionary of x ',default='./train_results/rl_x.pik')
parser.add_argument('--save_model_path_o',type=str, help='path where you want save the dictionary of o ',default='./train_results/rl_o.pik')
parser.add_argument('--train',type=bool, help='if you want train the dictionary', default= False)
parser.add_argument('--max_steps',type=int, help='how many epoch for train the dictionary',default=10000)
parser.add_argument('--player',type=int, help='select if you want to be player 1 or player 2, or put 0 if you want test with both', default= 0,choices=[0,1,2])
args = parser.parse_args()

if __name__ == '__main__':
    g = Game()
    
    if args.strategy==1:
        print("Testing min max... ")
        test_min_max(args)
    elif args.strategy==2:
        print("Testing reinforcment learning... ")

        test_rl(args)
    else:
        print("Testing min max... ")
        test_min_max(args)

        print("Testing reinforcment learning... ")

        test_rl(args)

