class BoardUtils:
    def __init__(self):
        self.row = [0, 0, 0]
        self.col = [0, 0, 0]
        self.first_diagonal = 0
        self.second_diagonal = 0

    def __analyze_board_state(self, board, n):
        for i in range(n):
            for j in range(n):
                if board[i][j] is not None:
                    self.row[i] += 1 if board[i][j] == "X" else -1
                    self.col[j] += 1 if board[i][j] == "X" else -1
                    if i == j:
                        self.first_diagonal += 1 if board[i][j] == "X" else -1
                    if i+j == n-1:
                        self.second_diagonal += 1 if board[i][j] == "X" else -1

    def get_winner(self, board):
        n = len(board)
        self.__init__()
        self.__analyze_board_state(board, n)
        if self.first_diagonal == n or self.second_diagonal == n:
            return "X"
        elif self.first_diagonal == (n * -1) or self.second_diagonal == (n * -1):
            return "O"
        for i in range(n):
            if self.row[i] == n or self.col[i] == n:
                return "X"
            elif self.row[i] == (n * -1) or self.col[i] == (n * -1):
                return "O"
        return None