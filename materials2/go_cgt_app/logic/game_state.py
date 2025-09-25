import copy

class GameState:
    def __init__(self, board, turn=1):
        self.board = copy.deepcopy(board)  # 2D list
        self.turn = turn  # 1=black, 2=white

    def get_legal_moves(self):
        size = len(self.board)
        moves = []
        for i in range(size):
            for j in range(size):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves

    def play_move(self, move):
        i, j = move
        new_state = GameState(self.board, 3 - self.turn)
        new_state.board[i][j] = self.turn
        return new_state
