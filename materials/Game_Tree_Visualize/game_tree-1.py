import csv
import graphviz
import hashlib

class GameState:
    """
    一つの囲碁の局面を管理するクラス。
    盤面データ、手番、そしてその局面のユニークなIDを持つ。
    """
    def __init__(self, board_data, turn=1):
        # 盤面データは不変（immutable）なタプルのタプルとして保持する
        self.board = tuple(map(tuple, board_data))
        self.turn = turn  # 1: 黒, -1: 白
        self.size = len(self.board)
        self.id = self._generate_id()

    def _generate_id(self):
        """盤面データからユニークなハッシュIDを生成する"""
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        return hashlib.sha1(board_str.encode()).hexdigest()[:8]

    def generate_moves(self):
        """
        現在の局面から可能な全ての手を生成し、
        新しいGameStateオブジェクトのリストとして返す。
        """
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:  # 空点にのみ着手可能
                    # 新しい盤面データを作成
                    new_board_list = [list(row) for row in self.board]
                    new_board_list[r][c] = self.turn
                    
                    # 次の手番で新しいGameStateオブジェクトを作成
                    next_turn = -self.turn
                    moves.append(GameState(new_board_list, next_turn))
        return moves
        
    def __str__(self):
        """盤面を簡易的な文字列で表現する（デバッグ用）"""
        chars = {1: 'B', -1: 'W', 0: '.'}
        return "\n".join("".join(chars[cell] for cell in row) for row in self.board)


def build_tree(start_node, max_depth, visited_ids):
    """
    開始局面から再帰的にゲーム木を構築する。
    max_depth: 読み進める手の深さ
    visited_ids: 同じ局面を複数回展開しないためのIDセット
    """
    if start_node.id in visited_ids or max_depth == 0:
        return

    visited_ids.add(start_node.id)
    
    # 子ノード（次の手の局面）を生成
    start_node.children = start_node.generate_moves()

    # 各子ノードについて再帰的に木を構築
    for child in start_node.children:
        build_tree(child, max_depth - 1, visited_ids)


def visualize_tree(root_node, dot):
    """
    構築されたゲーム木のデータから、Graphvizの描画命令を生成する。
    """
    # 現在のノードをGraphvizに追加
    dot.node(root_node.id, label=str(root_node), shape='box', fontname="monospace")

    # 子ノードがあれば、それらへのエッジを追加し、再帰的に描画
    if hasattr(root_node, 'children'):
        for child in root_node.children:
            # エッジの色を手番で分ける
            edge_color = "black" if root_node.turn == 1 else "white"
            dot.edge(root_node.id, child.id, color=edge_color)
            visualize_tree(child, dot)


def main():
    # --- 設定項目 ---
    CSV_FILE_PATH = 'board.csv'  # 入力するCSVファイルのパス
    MAX_DEPTH = 2               # 何手先まで読み進めるか (大きくしすぎると巨大な画像になるので注意)
    OUTPUT_IMAGE_PATH = 'game_tree' # 出力する画像ファイル名 (拡張子なし)

    # --- 実行処理 ---
    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return
    except Exception as e:
        print(f"エラー: CSVファイルの読み込み中に問題が発生しました: {e}")
        return

    # 開始局面（ルートノード）を作成
    start_node = GameState(board_data, turn=1) # 開始手番を黒(1)に設定

    # ゲーム木をメモリ上に構築
    print("ゲーム木を構築中...")
    build_tree(start_node, MAX_DEPTH, set())
    print("構築完了。")

    # Graphvizオブジェクトを作成
    dot = graphviz.Digraph(comment='Go Game Tree')
    dot.attr('node', style='filled', fillcolor='lightyellow')
    dot.attr(bgcolor='lightblue')

    # ゲーム木をGraphvizで描画
    print("ツリーを可視化中...")
    visualize_tree(start_node, dot)
    print("可視化完了。")
    
    # ファイルに保存
    try:
        dot.render(OUTPUT_IMAGE_PATH, format='png', view=True)
        print(f"ゲーム木を {OUTPUT_IMAGE_PATH}.png として保存し、表示しました。")
    except graphviz.backend.ExecutableNotFound:
        print("エラー: Graphvizが見つかりません。")
        print("ステップ0に従ってGraphvizソフトウェアをインストールし、PATHが通っているか確認してください。")
    except Exception as e:
        print(f"エラー: 画像の保存中に問題が発生しました: {e}")


if __name__ == "__main__":
    main()