from game import Game
from copy import deepcopy
import sys
import numpy as np

def calculate_occurences(board, player_id):
    occCount = 0
    for i in range(5):
        row = board[i, :]
        col = board[:, i]
        x = np.where(row == player_id)[0]
        y = np.where(col == player_id)[0]

        if len(x) == 4:
            ok = (x[-1] - x[0] == len(x) - 1)
            if ok:
                occCount += 1

        if len(y) == 4:
            ok = y[-1] - y[0] == len(y) - 1
            if ok:
                occCount += 1
    return occCount

def fitness(game, player_id, depth):
    winner = game.check_winner()

    if winner == 0:     ## Maximizer won (X)
        return 100 + depth
    elif winner == 1:   ## Minimizer won (O)
        return -100 - depth
    else:
        value = 0
        board = game.get_board()
        occValue = calculate_occurences(board, player_id) * 5

        if board[2, 2] == 0:
            value += 20
        elif board[2, 2] == 1:
            value -= 20

        if player_id == 1:
            occValue *= -1

        frequency = np.unique(board, return_counts=True)
        uniqueCount = len(frequency[0])
        if uniqueCount == 3:      ## Contains blank pieces
            maximizerPieceCount = frequency[1][1]
            minimizerPieceCount = frequency[1][2]
        elif uniqueCount == 2:
            maximizerPieceCount = frequency[1][0]
            minimizerPieceCount = frequency[1][1]

        value += (maximizerPieceCount - minimizerPieceCount) + occValue
        return value

def wrap_min_max(game: Game):
    return minmax(game, game.get_current_player())[0]

def minmax(game, player_id, alpha=-sys.maxsize, beta=sys.maxsize, depth=2):
    winner = game.check_winner()
    
    if winner != -1 or depth == 0:
        score = fitness(game, player_id, depth)
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