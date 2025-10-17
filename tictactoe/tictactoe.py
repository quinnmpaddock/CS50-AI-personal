"""
Tic Tac Toe Player
"""

import math
import copy

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
    numX = 0
    numO = 0
    
    # count num of Xs and Os
    for row in board:
        for cell in row:
            if cell == X:
                numX += 1
            elif cell == O:
                numO += 1

    if numX == numO:
        return X
    return O


    #raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                actions.add((i,j))

    return actions
    #raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #validate action
    if action == None:
        raise ValueError("Must choose an action")

    i, j = action
    try:
        if board[i][j] != EMPTY:
            raise ValueError("Invalid action: cell is already occupied")
        if not (0 <= i < 3 and 0 <= j < 3):
            raise ValueError("Invalid action: cell is out of bounds")
    except IndexError:
        raise ValueError("Invalid action: cell is out of bounds")

    #copy board
    board_copy = copy.deepcopy(board)
    
    #apply the correct player's move to the board
    current = player(board_copy)
    board_copy[i][j] = current

    return board_copy
    #raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    lines = []
    
    # horizontal/vertical win conditions
    for i in range(3):
        lines.append([board[i][0], board[i][1], board[i][2]])
        lines.append([board[0][i], board[1][i], board[2][i]])
        
    # diagonal win conditions
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[2][0], board[1][1], board[0][2]])
    
    for line in lines:
        if line == [X, X, X]:
            return X
        elif line == [O, O, O]:
            return O

    return None

    
    #raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # check for win condition
    if winner(board) is not None:
        return True
    
    # check for empty cells
    for row in board:
        if EMPTY in row:
            return False
    return True
        

    #raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    return 0
    
    #raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    def max_val(board):
        if terminal(board):
            return utility(board), None

        best = (-math.inf, None)

        for action in actions(board):
            score, _ = min_val(result(board, action))
            if score > best[0]:
                best = (score, action)

        return best

    def min_val(board):
        if terminal(board):
            return utility(board), None
        
        worst = (math.inf, None)

        for action in actions(board):
            score, _ = max_val(result(board, action))
            if score < worst[0]:
                worst = (score, action)

        return worst

    if player(board) == X:
        _, action = max_val(board)
        return action
    else:
        _, action = min_val(board)
        return action
        


    
    

    #raise NotImplementedError



    
    

