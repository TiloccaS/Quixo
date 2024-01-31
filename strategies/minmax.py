import sys
import numpy as np
from game import Game
from copy import deepcopy

def calculate_occurences(board, player_id):
    occCount = 0
    for i in range(5):
        row = board[i, :]
        col = board[:, i]
        x = np.where(row == player_id)[0]
        y = np.where(col == player_id)[0]

        if len(x) == 4:
            ok = (x[-1]!= player_id or x[0] != player_id)       ## means that there are 4 consecutive checkers
            if ok:
                occCount += 1

        if len(y) == 4:
            ok = (y[-1]!= player_id or y[0] != player_id)       ## means that there are 4 consecutive checkers
            if ok:
                occCount += 1

    diag_princ = [board[x, x] for x in range(board.shape[0])]
    z = np.where(diag_princ == player_id)
  
    if len(z) == 4:
            ok = (z[-1] != player_id or z[0] != player_id)
            if ok:
                occCount += 1

    diag_sec = [board[x, -(x + 1)] for x in range(board.shape[0])]
    t = np.where(diag_sec == player_id)

    if len(t) == 4:
            ok = (t[-1] != player_id or t[0] != player_id)
            if ok:
                occCount += 1
  
    return occCount

def fitness(game, player_id):
    winner = game.check_winner()

    if winner == 0:     ## Maximizer won (X)
        return 100 
    elif winner == 1:   ## Minimizer won (O)
        return -100 
    else:
        ## if there isn't a winner we search evaluate using the occurences that there are in row or column or diagonal
        value = 0
        board = game.get_board()
        occValue = calculate_occurences(board, player_id) * 5
        
        ## if you take the center of board you have a little reward
        if board[2, 2] == 0:
            value += 20
        elif board[2, 2] == 1:
            value -= 20

        if player_id == 1:
            occValue *= -1

        frequency = np.unique(board, return_counts=True)
        uniqueCount = len(frequency[0])     ## in position 0 there are [-1(if there are space not picked), 0, 1]
        if uniqueCount == 3:        ## it means that there are position not selected yet     
            xPieceCount = frequency[1][1]
            oPieceCount = frequency[1][2]
        elif uniqueCount == 2:      ## it means that all position are picked
            xPieceCount = frequency[1][0]
            oPieceCount = frequency[1][1]

        value += (xPieceCount - oPieceCount) + occValue
        return value

def wrap_min_max(game: Game):
    return minmax(game, game.get_current_player())[0]

def minmax(game, player_id, alpha=-sys.maxsize, beta=sys.maxsize, depth=2):
    winner = game.check_winner()
    
    if winner != -1 or depth == 0:
        score = fitness(game, player_id)
        return None, score

    best_ply = None
    possible_moves = game.getPossibleMoves(player_id) 
    
    if player_id == 0:      ## Player X 
        new_player_id = 1

        for ply in possible_moves:
            tmp = deepcopy(game)
            tmp.move(ply[0], ply[1], player_id)
            _, val = minmax(tmp, new_player_id, alpha, beta, depth - 1)

            if val > alpha:
                alpha = val
                best_ply = ply
            
            if alpha >= beta:
                break

        return best_ply, alpha
    
    else:       ## Player O
        new_player_id = 0

        for ply in possible_moves:
            tmp = deepcopy(game)
            tmp.move(ply[0], ply[1], player_id)
            _, val = minmax(tmp, new_player_id, alpha, beta, depth - 1)

            if val < beta:
                beta = val
                best_ply = ply
            
            if alpha >= beta:
                break
            
        return best_ply, beta