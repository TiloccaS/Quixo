import random
import dill
from game import Game, Move, Player
from strategies.rl import Q_learing, CustomState,  get_coordinates, costruisci_array,print_dictionary
from copy import deepcopy
from strategies.utils import CustomGame
from tqdm.auto import tqdm
class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        #print("turn random")
        return from_pos, move


class MyPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move
    
class RLPlayer(Player):
    def __init__(self, learning_rate=0.1, discount_factor=0.7, pretrain_path_x=None,pretrain_path_o=None, save_model_path_x=None,save_model_path_o=None, max_steps=None, train=False) -> None:
        super().__init__()
        if train:
            ql = Q_learing(learning_rate, discount_factor, pretrain_path_x=pretrain_path_x,pretrain_path_o=pretrain_path_x, max_steps=max_steps)
            steps, self.value_dictionary_x = ql.train()
            self.value_dictionary_o=self.value_dictionary_x
            if save_model_path_x is not None:
                print(len(self.value_dictionary_x))
                d = {'steps': steps/2, 'value_dictionary': self.value_dictionary_x}

                with open(save_model_path_x, 'wb') as outfile:
                    dill.dump(d, outfile)
            if save_model_path_o is not None:
                print(len(self.value_dictionary_o))
                d = {'steps': steps/2, 'value_dictionary': self.value_dictionary_o}

                with open(save_model_path_o, 'wb') as outfile:
                    dill.dump(d, outfile)
        elif not train and pretrain_path_x is not None and pretrain_path_o is not None:
            with open(pretrain_path_x, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary_x = d['value_dictionary']
            print(len(self.value_dictionary_x))
            with open(pretrain_path_o, 'rb') as f:
                d = dill.load(f)

            self.value_dictionary_o = d['value_dictionary']
            print(len(self.value_dictionary_o))
        
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        game_tmp=CustomGame(game)
        current_state = CustomState(get_coordinates(game_tmp.get_board()))
        current_state.state=current_state.get_equivalent()
        game_tmp.modify_board(costruisci_array(deepcopy(current_state.state)))

        #print_dictionary(self.value_dictionary)
        if game_tmp.get_current_player==0:
                value_dictionary=self.value_dictionary_x

        else:
                value_dictionary=self.value_dictionary_o
        if current_state in value_dictionary:
            

            list_action = sorted(value_dictionary[current_state], key=value_dictionary[current_state].get)
            if len(list_action)>0:
                action = list_action[0].split('-')
                #print(action[0])
                from_pos =tuple( (int(c) for c in action[0] if c.isdigit()))
                #print(from_pos)

                #game_tmp.print()
                if action[1] == 'Move.LEFT':
                    move = Move.LEFT
                elif action[1] == 'Move.RIGHT':
                    move = Move.RIGHT
                elif action[1] == 'Move.TOP':
                    move = Move.TOP
                else:
                    move = Move.BOTTOM
                game._board=game_tmp._board
                ok= game_tmp.move(from_pos=from_pos,slide=move,player_id=game_tmp.current_player_idx)
                if ok==False:
                    game.print()
                    print(move,from_pos,ok,game.get_current_player())

                if from_pos==tuple((0,4)) or from_pos==tuple((4,0)) :
                    from_pos = (random.randint(0, 4), random.randint(0, 4))
                    move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
            else:
                 from_pos = (random.randint(0, 4), random.randint(0, 4))
                 move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])

        else:
            ## Random play
            #print("random")
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
       # print("ended")
        return from_pos, move
    
player1 = RLPlayer(save_model_path_x='rl_x.pik',save_model_path_o='rl_o.pik',max_steps=100,train=True)
player2 = RandomPlayer()

print('Testing')

win = 0
lose = 0
draw = 0
for i in tqdm(range(900)):
    #print(i)
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