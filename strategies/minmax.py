from game import Game,Move
from copy import deepcopy
import sys
import numpy as np
def wrap_min_max(board, player_id):
    return minmax(board,player_id)[0]
def minmax(board, player_id, depth=4, alpha=-sys.maxsize, beta=sys.maxsize):
    val = board.check_winner()
    best_ply = None
    possible = board.getPossibleMoves(player_id)

    if val != -1 or not possible or depth == 0:
        if val == 0:
            val = float('inf')
        elif val == 1:
            val = float('-inf')
        return best_ply, val

    #evaluations = list()
    prev_player_id = player_id

    if player_id == 1:
        val = float('inf')
        player_id = 0
    else:
        val = float('-inf')
        player_id = 1

    for ply in possible:
        tmp = deepcopy(board)
        acc = tmp.move(ply[0], ply[1], prev_player_id)

        if acc == False:
            print(acc, player_id, "con mosse :", ply, "\n", board.get_board())
        
        _, tmp1 = minmax(tmp, player_id, depth - 1, -beta, -alpha)
        #evaluations.append((ply, -val))
        if tmp1 > val:
            val = tmp1
            best_ply = ply

        alpha = max(alpha, -val)
        
        if alpha >= beta:
            break  # Taglio beta
   
    #print(best_ply, val)
    return best_ply, -val#max(evaluations, key=lambda k: k[1])

if __name__ == '__main__':
    from strategies.utils import CustomGame
    from strategies.utils import MinMaxPlayer,RandomPlayer
    cnt=0
    for i in range(100):
        game=CustomGame()
        player1=MinMaxPlayer()
        player2=RandomPlayer()
        winner=game.play(player1,player2)
        if winner==1:
            cnt+=1
    
    print(cnt)