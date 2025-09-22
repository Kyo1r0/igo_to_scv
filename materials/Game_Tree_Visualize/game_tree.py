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
    # --- 変更点(1): last_move属性を追加 ---
    def __init__(self, board_data, turn=1, last_move=None):
        self.board = tuple(map(tuple, board_data))
        self.turn = turn
        self.size = len(self.board)
        self.last_move = last_move # この局面に至った直前の着手座標 (row, col)
        self.id = self._generate_id()

    def _generate_id(self):
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        turn_str = str(self.turn)
        # ID生成にlast_moveの情報も加える
        last_move_str = str(self.last_move)
        return hashlib.sha1((board_str + turn_str + last_move_str).encode()).hexdigest()[:10]

    def generate_moves(self):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    new_board_list = [list(row) for row in self.board]
                    new_board_list[r][c] = self.turn
                    next_turn = -self.turn
                    # --- 変更点(2): 新しいGameStateにlast_moveを渡す ---
                    moves.append(GameState(new_board_list, next_turn, last_move=(r, c)))
        return moves

def create_node_image(node, file_path):
    """
    GameStateオブジェクトから盤面のPNG画像を生成する。
    """
    padding = 5
    cell_size = 15
    stone_radius = 6
    img_size = cell_size * (node.size - 1) + 2 * padding
    
    image = Image.new("RGB", (img_size, img_size), "#D1B48C")
    drawer = ImageDraw.Draw(image)

    start = padding
    end = cell_size * (node.size - 1) + padding
    for i in range(node.size):
        pos = start + i * cell_size
        drawer.line([(start, pos), (end, pos)], fill="black")
        drawer.line([(pos, start), (pos, end)], fill="black")

    for r in range(node.size):
        for c in range(node.size):
            stone = node.board[r][c]
            if stone != 0:
                x = padding + c * cell_size
                y = padding + r * cell_size
                color = "black" if stone == 1 else "white"
                bbox = (x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius)
                drawer.ellipse(bbox, fill=color, outline="black")
    
    # --- 変更点(3): 直前の着手を強調表示するロジック ---
    if node.last_move is not None:
        r, c = node.last_move
        x = padding + c * cell_size
        y = padding + r * cell_size
        
        # 強調表示用の赤い四角を描画
        highlight_offset = stone_radius + 2
        drawer.rectangle(
            (x - highlight_offset, y - highlight_offset, x + highlight_offset, y + highlight_offset),
            outline="red", 
            width=2 
        )

    # 手番を示すインジケーターを描画
    indicator_radius = 4
    indicator_padding = 6
    indicator_x = img_size - indicator_padding
    indicator_y = indicator_padding
    indicator_color = "black" if node.turn == 1 else "white"
    indicator_bbox = (
        indicator_x - indicator_radius, indicator_y - indicator_radius,
        indicator_x + indicator_radius, indicator_y + indicator_radius,
    )
    drawer.ellipse(indicator_bbox, fill=indicator_color, outline="black")
    
    image.save(file_path)

def build_tree(start_node, max_depth, visited_ids):
    if start_node.id in visited_ids or max_depth == 0:
        return

    visited_ids.add(start_node.id)
    start_node.children = start_node.generate_moves()

    for child in start_node.children:
        build_tree(child, max_depth - 1, visited_ids)

def visualize_tree(root_node, dot, node_img_dir, visited_ids_viz):
    if root_node.id in visited_ids_viz:
        return
    visited_ids_viz.add(root_node.id)

    image_path = os.path.join(node_img_dir, f"{root_node.id}.png")
    
    if not os.path.exists(image_path):
        create_node_image(root_node, image_path)

    dot.node(root_node.id, label='', image=image_path, shape='box')

    if hasattr(root_node, 'children'):
        for child in root_node.children:
            edge_color = "black" if root_node.turn == 1 else "gray"
            dot.edge(root_node.id, child.id, color=edge_color)
            visualize_tree(child, dot, node_img_dir, visited_ids_viz)

def main():
    CSV_FILE_PATH = 'board_yose.csv'
    MAX_DEPTH = 3
    OUTPUT_IMAGE_PATH = 'game_tree'
    NODE_IMAGE_DIR = 'game_tree_nodes'

    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return
    
    os.makedirs(NODE_IMAGE_DIR, exist_ok=True)

    # 開始局面にはlast_moveがない（デフォルトのNoneが使われる）
    start_node = GameState(board_data, turn=1)

    print("ゲーム木を構築中...")
    build_tree(start_node, MAX_DEPTH, set())
    print("構築完了。")

    dot = graphviz.Digraph(comment='Go Game Tree')
    dot.attr('node', style='filled', fillcolor='white')
    dot.attr(bgcolor='lightgray', rankdir='TB')

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

