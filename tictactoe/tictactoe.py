"""
Tic Tac Toe Player
"""
import copy
from selectors import SelectSelector

import BoardUtils as bu

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
    x_player_count = 0
    o_player_count = 0
    n = len(board)
    for i in range(n):
        for j in range(n):
            if board[i][j] == X:
                x_player_count += 1
            elif board[i][j] == O:
                o_player_count += 1
    if x_player_count == 0 and o_player_count == 0:
        return X
    return X if x_player_count <= o_player_count else O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    n = len(board)
    possible_actions = set()
    for i in range(n):
        for j in range(n):
            if board[i][j] is None:
                possible_actions.add((i, j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action is None or (action[0] < 0 or action[0] >= 3) or (action[1] < 0 or action[1] >= 3):
        print(board)
        raise RuntimeError("Invalid Action")
    new_board = copy.deepcopy(board)
    if board[action[0]][action[1]] is not None:
        raise RuntimeError("Invalid action")
    new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    return bu.BoardUtils().get_winner(board)

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    n = len(board)
    champion = utility(board)
    if champion != 0:
        return True
    for i in range(n):
        for j in range(n):
            if board[i][j] is None:
                return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    champion = bu.BoardUtils().get_winner(board)
    if champion is X:
        return 1
    elif champion is O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    best_action = None
    if terminal(board):
        print("Board is in terminal state {}", board)
        return None
    ai_player = player(board)
    # when AI is 'X' then the algo picks the max of least  optimal steps of O
    if ai_player is X:
        max_score = float('-inf')
        for action in actions(board):
            new_board = result(board, action)
            score = min_value(new_board)
            if score > max_score:
                max_score = score
                best_action = action
    # when AI is 'O' then the algo picks the min of best optimal steps of X
    else:
        min_score = float('inf')
        for action in actions(board):
            new_board = result(board, action)
            score = max_value(new_board)
            if score < min_score:
                min_score = score
                best_action = action
    return best_action


# Player who tries to minimize utility for X
# the best optimal scores of O
def min_value(board):
    if terminal(board):
        return utility(board)
    min_score = float('inf')
    for possible_action in actions(board):
        new_board = result(board, possible_action)
        min_score = min(min_score, max_value(new_board))
    return min_score

# Player who tries to maximize utility for X
# the best optimal scores of X
def max_value(board):
    if terminal(board):
        return utility(board)
    max_score = float('-inf')
    for possible_action in actions(board):
        new_board = result(board, possible_action)
        max_score = max(max_score, min_value(new_board))
    return max_score
