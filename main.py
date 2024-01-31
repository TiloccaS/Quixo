import random
import dill
import argparse
from copy import deepcopy
from game import Game, Move, Player
from strategies.minmax import wrap_min_max
from strategies.utils import CustomGame, test
from strategies.rl import Q_learing, CustomState, get_coordinates, build_board_from_coordinates

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
    def __init__(self, learning_rate=0.1, discount_factor=0.7, pretrain_path_x=None, pretrain_path_o=None, 
            save_model_path_x=None, save_model_path_o=None, max_steps=None, train=False) -> None:
        super().__init__()

        if train:
            ql = Q_learing(learning_rate, discount_factor, pretrain_path_x=pretrain_path_x, pretrain_path_o=pretrain_path_o, max_steps=max_steps)
            steps, self.value_dictionary_x, self.value_dictionary_o = ql.train()

            if save_model_path_x is not None:
                print('Saving dictionary of x...')
                d = {'steps': steps/2, 'value_dictionary': self.value_dictionary_x}

                with open(save_model_path_x, 'wb') as outfile_x:
                    dill.dump(d, outfile_x)

            if save_model_path_o is not None:
                print('Saving dictionary of o...')
                d = {'steps': steps/2, 'value_dictionary': self.value_dictionary_o}

                with open(save_model_path_o, 'wb') as outfile_o:
                    dill.dump(d, outfile_o)

        elif not train and pretrain_path_x is not None and pretrain_path_o is not None:
            print('Reading dictionary of x...')
            with open(pretrain_path_x, 'rb') as f:
                d = dill.load(f)
            self.value_dictionary_x = d['value_dictionary']

            print('Reading dictionary of o...')
            with open(pretrain_path_o, 'rb') as f:
                d = dill.load(f)
            self.value_dictionary_o = d['value_dictionary']
        
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        game_tmp = CustomGame(game)
        current_state = CustomState(get_coordinates(game_tmp.get_board()))
        current_state.state = current_state.get_equivalent()

        ## we use the equivalent represention of the board to extract the equivalent move
        game_tmp.modify_board(build_board_from_coordinates(deepcopy(current_state.state)))  
            
        if game.get_current_player() == 0:
            value_dictionary = self.value_dictionary_x
        else:
            value_dictionary = self.value_dictionary_o

        if current_state in value_dictionary:
            if game.get_current_player()==0:
                list_action = sorted(value_dictionary[current_state], key=value_dictionary[current_state].get,reverse=True)
            else:
                list_action = sorted(value_dictionary[current_state], key=value_dictionary[current_state].get)

            if len(list_action) > 0:
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

                game._board = game_tmp._board
           
            else:
                 from_pos = (random.randint(0, 4), random.randint(0, 4))
                 move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])

        else:
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
            
        return from_pos, move


parser = argparse.ArgumentParser(description='Descrizione del tuo script.')
parser.add_argument('--strategy', type=int, help='strategy 0: both, strategy1: minmax, strategy 2: rl', default=0)
parser.add_argument('--pretrain_path_o', type=str, help='pretrain path of dictionary o', default=None)
parser.add_argument('--pretrain_path_x', type=str, help='pretrain path of dictionary x', default=None)
parser.add_argument('--save_model_path_x',type=str, help='path where you want save the dictionary of x ', default='./train_results/rl_x.pik')
parser.add_argument('--save_model_path_o',type=str, help='path where you want save the dictionary of o ', default='./train_results/rl_o.pik')
parser.add_argument('--train', type=bool, help='if you want train the dictionary', default=False)
parser.add_argument('--max_steps', type=int, help='how many epoch for train the dictionary', default=10000)
parser.add_argument('--player', type=int, 
    help='select if you want to be player 1 or player 2, or put 0 if you want test with both', default=0, choices=[0,1,2])
parser.add_argument('--num_games', type=int, help='how many games to test strategy', default=1000)
args = parser.parse_args()

if __name__ == '__main__':
    player1 = RandomPlayer()
    num_games = args.num_games

    if args.strategy == 1:
        player2 = MinMaxPlayer()

        if args.player == 1:
            print('\nMinMaxPlayer vs RandomPlayer: ')
            win, lose, draw = test(player2, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}      draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        elif args.player == 2:
            print('\nRandomPlayer vs MinMaxPlayer: ')
            lose, win, draw = test(player1, player2, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        else:
            print('\nMinMaxPlayer vs RandomPlayer: ')
            win, lose, draw = test(player2, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRandomPlayer vs MinMaxPlayer: ')
            lose, win, draw = test(player1, player2, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

    elif args.strategy == 2:
        player2 = RLPlayer(pretrain_path_x=args.pretrain_path_x, pretrain_path_o=args.pretrain_path_o, save_model_path_x=args.save_model_path_x,
            save_model_path_o=args.save_model_path_o, max_steps=args.max_steps, train=args.train)
        
        if args.player == 1:
            print('\nRLPlayer vs RandomPlayer: ')
            win, lose, draw = test(player2, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        elif args.player == 2:
            print('\nRandomPlayer vs RLPlayer: ')
            lose, win, draw = test(player1, player2, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        else:
            print('\nRLPlayer vs RandomPlayer: ')
            win, lose, draw = test(player2, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRandomPlayer vs RLPlayer: ')
            lose, win, draw = test(player1, player2, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        
    else:
        player2 = MinMaxPlayer()
        player3 = RLPlayer(pretrain_path_x=args.pretrain_path_x, pretrain_path_o=args.pretrain_path_o, save_model_path_x=args.save_model_path_x,
            save_model_path_o=args.save_model_path_o, max_steps=args.max_steps, train=args.train)
        
        if args.player == 1:
            print('\nMinMaxPlayer vs RandomPlayer: ')
            win, lose, draw = test(player2, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRLPlayer vs RandomPlayer: ')
            win, lose, draw = test(player3, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        elif args.player == 2:
            print('\nRandomPlayer vs MinMaxPlayer: ')
            lose, win, draw = test(player1, player2, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRandomPlayer vs RLPlayer: ')
            lose, win, draw = test(player1, player3, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        else:
            print('\nMinMaxPlayer vs RandomPlayer: ')
            win, lose, draw = test(player2, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRandomPlayer vs MinMaxPlayer: ')
            lose, win, draw = test(player1, player2, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRLPlayer vs RandomPlayer: ')
            win, lose, draw = test(player3, player1, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))

            print('\nRandomPlayer vs RLPlayer: ')
            lose, win, draw = test(player1, player3, num_games)
            win_rate = win / (win + lose + draw)
            print('win: {0}     lose: {1}     draw: {2}     win rate: {3:.2%}'.format(win, lose, draw, win_rate))
        

