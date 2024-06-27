"""
Tic Tac Toe Player
"""

import math
import copy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for row in board:
        count += row.count(EMPTY)

    return X if count % 2 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                moves.add((i, j))

    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if not (0 <= i <= 2 and 0 <= j <= 2):
        raise ValueError
    if board[i][j] != EMPTY:
        raise Exception("Invalid Action")

    newBoard = copy.deepcopy(board)
    newBoard[i][j] = player(board)
    return newBoard 


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows and columns    
    for i in range(3):
        if board[i][0] is not EMPTY and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
        if board[0][i] is not EMPTY and board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]
            
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]:
        return board[1][1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or not any(EMPTY in row for row in board)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    mark = winner(board)
    return 1 if mark == X else -1 if mark == O else 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    scores = []
    available_actions = actions(board)
    turn = player(board)

    for action in available_actions:
        newBoard = result(board, action)
        score = _minimax(newBoard, -math.inf, math.inf)
        scores.append(score)
        
    best_score = max(scores) if turn == X else min(scores)
    best_actions = [action for i, action in enumerate(available_actions) if scores[i] == best_score]

    return random.choice(best_actions)

def _minimax(board, alpha, beta):
    if terminal(board):
        return utility(board)

    turn = player(board)
    best_score = -math.inf if turn == X else math.inf

    for action in actions(board):
        newBoard = result(board, action)
        args = (best_score, _minimax(newBoard, alpha, beta))
        best_score = max(args) if turn == X else min(args)

        if turn == X:
            alpha = max(alpha, best_score)
        else:
            beta = min(beta, best_score)

        if alpha >= beta:
            break

    return best_score

