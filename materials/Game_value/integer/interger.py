import csv
import graphviz
import hashlib
import os

class GameValue:
    """
    ゲームの「値」を表現するためのクラス。
    将来的に様々な種類の値を追加できるように設計。
    """
    def __init__(self, value_type='UNKNOWN', value=None):
        self.type = value_type  # 'INTEGER', 'UNKNOWN'など
        self.value = value      # 整数値など

    def __repr__(self):
        """デバッグなどで見やすくするための文字列表現"""
        if self.type == 'INTEGER':
            return str(self.value)
        return '?' # 不明な値は'?'で表現

class GameState:
    """
    一つの囲碁の局面を管理するクラス。
    このクラスは「値」を持たず、純粋な盤面の状態のみを管理する。
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
        # --- ここからが変更点 ---
        # player_colorが1なら[0, 2]、-1なら[0, -2]のマスを探す
        allowed_empty_points = [0, player_color * 2]
        # --- 変更点はここまで ---

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
    """
    GameStateノードの値を再帰的に計算する。
    計算結果はmemoization_cacheに保存して再利用する。
    """
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

# --- 可視化のための関数群 ---
def build_and_visualize(start_node, max_depth, dot):
    if max_depth < 0 or not start_node or start_node.id in dot.body:
        return

    value = calculate_value(start_node)
    dot.node(start_node.id, label=f"Value: {value}")

    if max_depth == 0:
        return
        
    left_options = start_node.generate_moves_for_player(1)
    for child in left_options:
        dot.edge(start_node.id, child.id, color="black")
        build_and_visualize(child, max_depth - 1, dot)

    right_options = start_node.generate_moves_for_player(-1)
    for child in right_options:
        dot.edge(start_node.id, child.id, color="gray")
        build_and_visualize(child, max_depth - 1, dot)

def main():
    CSV_FILE_PATH = 'test2.csv'
    MAX_DEPTH = 3
    OUTPUT_IMAGE_PATH = 'game_tree_integer'

    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return

    start_node = GameState(board_data)

    dot = graphviz.Digraph(comment='Integer Game Value Tree')
    dot.attr(rankdir='TB')
    
    print("ゲーム木を構築し、値を計算中...")
    build_and_visualize(start_node, MAX_DEPTH, dot)
    print("計算完了。")
    
    try:
        dot.render(OUTPUT_IMAGE_PATH, format='png', view=True)
        print(f"整数値ゲーム木を {OUTPUT_IMAGE_PATH}.png として保存しました。")
    except graphviz.backend.ExecutableNotFound:
        print("エラー: Graphvizが見つかりません。")
    except Exception as e:
        print(f"エラー: 画像の保存中に問題が発生しました: {e}")

if __name__ == "__main__":
    main()
