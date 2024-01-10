from game import Game,Move
from copy import deepcopy
import sys
import numpy as np


def minmax(board, player_id, depth=5, alpha=-sys.maxsize, beta=sys.maxsize):
    val = board.check_winner()
    possible = board.getPossibleMoves(player_id)

    if val != -1 or not possible or depth == 0:
        if val == 0:
            val = -1
        return None, val

    evaluations = list()
    prev_player_id = player_id

    if player_id == 1:
        player_id = 0
    else:
        player_id = 1

    for ply in possible:
        tmp = deepcopy(board)
        acc = tmp.move(ply[0], ply[1], prev_player_id)

        if acc == False:
            print(acc, player_id, "con mosse :", ply, "\n", board.get_board())
        
        _, val = minmax(tmp, player_id, depth - 1, -beta, -alpha)
        evaluations.append((ply, -val))
        
        alpha = max(alpha, -val)
        
        if alpha >= beta:
            break  # Taglio beta
        
    return max(evaluations, key=lambda k: k[1])

if __name__ == '__main__':
   game=Game()
   game._board=np.array([[1, 0, 1, 0, 1],
                        [0, 1, 0, 1, 0],
                        [1, 0, 1, 0, 1],
                        [0, 1, 0, 1, 0],
                        [0, 1, 1, 1, 0 ]])
   print(minmax(game,1))