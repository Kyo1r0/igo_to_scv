import csv
import hashlib
import os

class GameValue:
    """
    ゲームの「値」を表現するためのクラス。
    """
    def __init__(self, value_type='UNKNOWN', value=None):
        self.type = value_type  # 'INTEGER', 'UNKNOWN'など
        self.value = value      # 整数値など

    def __repr__(self):
        if self.type == 'INTEGER':
            return str(self.value)
        return '?'


class GameState:
    """
    一つの囲碁の局面を管理するクラス。
    """
    def __init__(self, board_data):
        self.board = tuple(map(tuple, board_data))
        self.size = len(self.board)
        self.id = self._generate_id()

    def _generate_id(self):
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        return hashlib.sha1(board_str.encode()).hexdigest()[:10]

    def generate_moves_for_player(self, player_color):
        """
        指定された色のプレイヤーが着手可能な手を全て生成する。
        player_color: 1 (黒), -1 (白)
        """
        moves = []
        allowed_empty_points = [0, player_color * 2]

        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] in allowed_empty_points:
                    new_board_list = [list(row) for row in self.board]
                    new_board_list[r][c] = player_color
                    moves.append(GameState(new_board_list))
        return moves


# --- 値を計算するためのコアロジック ---
memoization_cache = {}

def calculate_value(node):
    if node.id in memoization_cache:
        return memoization_cache[node.id]

    left_options = node.generate_moves_for_player(1)
    right_options = node.generate_moves_for_player(-1)
    
    left_values = {calculate_value(child) for child in left_options}
    right_values = {calculate_value(child) for child in right_options}

    # 終局: 0 = { | }
    if not left_options and not right_options:
        result = GameValue('INTEGER', 0)
        memoization_cache[node.id] = result
        return result

    all_children_are_integers = all(v.type == 'INTEGER' for v in left_values | right_values)

    if all_children_are_integers:
        # 正の整数: n = { n-1 | }
        if len(left_values) == 1 and not right_values:
            child_value = list(left_values)[0].value
            result = GameValue('INTEGER', child_value + 1)
            memoization_cache[node.id] = result
            return result
            
        # 負の整数: -n = { | 1-n }
        if not left_values and len(right_values) == 1:
            child_value = list(right_values)[0].value
            result = GameValue('INTEGER', child_value - 1)
            memoization_cache[node.id] = result
            return result

    result = GameValue('UNKNOWN')
    memoization_cache[node.id] = result
    return result


# --- 値を出力する関数 ---
def dump_game_values(node, max_depth, f, depth=0, visited=None):
    if visited is None:
        visited = set()
    if node.id in visited or depth > max_depth:
        return
    visited.add(node.id)

    value = calculate_value(node)
    f.write(f"Depth {depth}, ID {node.id}, Value: {value}\n")

    for child in node.generate_moves_for_player(1):
        dump_game_values(child, max_depth, f, depth+1, visited)
    for child in node.generate_moves_for_player(-1):
        dump_game_values(child, max_depth, f, depth+1, visited)


def main():
    CSV_FILE_PATH = 'test2.csv'
    MAX_DEPTH = 3

    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return

    start_node = GameState(board_data)

    # 出力ファイル名を自動で決定
    base_name = os.path.splitext(CSV_FILE_PATH)[0]
    OUTPUT_FILE_PATH = f"{base_name}_value.txt"

    print("ゲーム木を構築し、値を計算中...")
    with open(OUTPUT_FILE_PATH, "w") as f:
        dump_game_values(start_node, MAX_DEPTH, f)
    print(f"計算完了。値を {OUTPUT_FILE_PATH} に保存しました。")


if __name__ == "__main__":
    main()
