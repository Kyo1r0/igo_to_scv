import csv
import graphviz
import hashlib
import os

# Pillow(PIL)ライブラリのインポート
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("エラー: Pillowライブラリが見つかりません。")
    print("コマンドプロンプトで pip install Pillow を実行してください。")
    exit()

class GameState:
    """
    一つの囲碁の局面を管理するクラス。
    盤面データ、手番、そしてその局面のユニークなIDを持つ。
    """
    def __init__(self, board_data, turn=1):
        self.board = tuple(map(tuple, board_data))
        self.turn = turn
        self.size = len(self.board)
        self.id = self._generate_id()

    def _generate_id(self):
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        turn_str = str(self.turn)
        # 手番の情報もIDに含めることで、同じ盤面でも手番が違えば別のノードとして扱える
        return hashlib.sha1((board_str + turn_str).encode()).hexdigest()[:10]

    def generate_moves(self):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    new_board_list = [list(row) for row in self.board]
                    new_board_list[r][c] = self.turn
                    next_turn = -self.turn
                    moves.append(GameState(new_board_list, next_turn))
        return moves

def create_node_image(node, file_path):
    """
    GameStateオブジェクトから盤面のPNG画像を生成する。
    """
    # 画像のサイズ設定
    padding = 5
    cell_size = 15
    stone_radius = 6
    img_size = cell_size * (node.size - 1) + 2 * padding
    
    # 画像オブジェクトと描画ツールを作成
    image = Image.new("RGB", (img_size, img_size), "#D1B48C")
    drawer = ImageDraw.Draw(image)

    # 格子線の描画
    start = padding
    end = cell_size * (node.size - 1) + padding
    for i in range(node.size):
        pos = start + i * cell_size
        drawer.line([(start, pos), (end, pos)], fill="black")
        drawer.line([(pos, start), (pos, end)], fill="black")

    # 石の描画
    for r in range(node.size):
        for c in range(node.size):
            stone = node.board[r][c]
            if stone != 0:
                x = padding + c * cell_size
                y = padding + r * cell_size
                color = "black" if stone == 1 else "white"
                bbox = (x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius)
                drawer.ellipse(bbox, fill=color, outline="black")
    
    # ファイルに保存
    image.save(file_path)

def build_tree(start_node, max_depth, visited_ids):
    if start_node.id in visited_ids or max_depth == 0:
        return

    visited_ids.add(start_node.id)
    start_node.children = start_node.generate_moves()

    for child in start_node.children:
        build_tree(child, max_depth - 1, visited_ids)

def visualize_tree(root_node, dot, node_img_dir, visited_ids_viz):
    """
    構築されたゲーム木のデータから、Graphvizの描画命令を生成する。
    ノードはテキストではなく、生成した画像ファイルを使用する。
    """
    if root_node.id in visited_ids_viz:
        return
    visited_ids_viz.add(root_node.id)

    # ノード用の画像ファイルパスを決定
    image_path = os.path.join(node_img_dir, f"{root_node.id}.png")
    
    # 画像がまだ生成されていなければ生成する
    if not os.path.exists(image_path):
        create_node_image(root_node, image_path)

    # Graphvizに画像ノードとして追加（labelは空にする）
    dot.node(root_node.id, label='', image=image_path, shape='box')

    if hasattr(root_node, 'children'):
        for child in root_node.children:
            edge_color = "black" if root_node.turn == 1 else "gray" # 白番の矢印を灰色に
            dot.edge(root_node.id, child.id, color=edge_color)
            visualize_tree(child, dot, node_img_dir, visited_ids_viz)

def main():
    # --- 設定項目 ---
    CSV_FILE_PATH = 'board_yose.csv'
    MAX_DEPTH = 3
    OUTPUT_IMAGE_PATH = 'game_tree'
    NODE_IMAGE_DIR = 'game_tree_nodes' # ノード画像を保存するディレクトリ

    # --- 実行処理 ---
    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return
    
    # ノード画像を保存するディレクトリを作成
    os.makedirs(NODE_IMAGE_DIR, exist_ok=True)

    start_node = GameState(board_data, turn=1)

    print("ゲーム木を構築中...")
    build_tree(start_node, MAX_DEPTH, set())
    print("構築完了。")

    dot = graphviz.Digraph(comment='Go Game Tree')
    dot.attr('node', style='filled', fillcolor='white')
    dot.attr(bgcolor='lightgray', rankdir='TB') # 上から下へのツリーレイアウト

    print("ツリーを可視化中（ノード画像を生成しています）...")
    visualize_tree(start_node, dot, NODE_IMAGE_DIR, set())
    print("可視化完了。")
    
    try:
        dot.render(OUTPUT_IMAGE_PATH, format='png', view=True)
        print(f"ゲーム木を {OUTPUT_IMAGE_PATH}.png として保存し、表示しました。")
    except graphviz.backend.ExecutableNotFound:
        print("エラー: Graphvizが見つかりません。")
        print("Graphvizソフトウェアをインストールし、PATHが通っているか確認してください。")
    except Exception as e:
        print(f"エラー: 画像の保存中に問題が発生しました: {e}")

if __name__ == "__main__":
    main()

