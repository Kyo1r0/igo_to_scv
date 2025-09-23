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
    def __init__(self, board_data, turn=1, last_move=None):
        self.board = tuple(map(tuple, board_data))
        self.turn = turn
        self.size = len(self.board)
        self.last_move = last_move
        self.id = self._generate_id()

    def _generate_id(self):
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        turn_str = str(self.turn)
        last_move_str = str(self.last_move)
        return hashlib.sha1((board_str + turn_str + last_move_str).encode()).hexdigest()[:10]

    def generate_moves(self):
        """
        現在の局面から可能な全ての手を生成する。
        CSVの2(黒専用), -2(白専用)のルールを考慮する。
        """
        moves = []
        player_color = self.turn
        
        for r in range(self.size):
            for c in range(self.size):
                point = self.board[r][c]
                
                # --- 変更点(1): 着手可能かどうかの判定ロジック ---
                # プレイヤーは共有の空点(0)か、自分の専用点(黒なら2, 白なら-2)に打てる
                can_play = (point == 0) or \
                           (player_color == 1 and point == 2) or \
                           (player_color == -1 and point == -2)
                
                if can_play:
                    new_board_list = [list(row) for row in self.board]
                    # 着手すると、その点は石になる
                    new_board_list[r][c] = player_color
                    
                    next_turn = -player_color
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
            point_data = node.board[r][c]
            x = padding + c * cell_size
            y = padding + r * cell_size

            # 石と専用点の描画
            if point_data == 1 or point_data == -1:
                color = "black" if point_data == 1 else "white"
                drawer.ellipse((x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius), fill=color, outline="black")
            elif point_data == 2 or point_data == -2:
                color = "black" if point_data == 2 else "white"
                marker_size = 4
                drawer.rectangle((x - marker_size, y - marker_size, x + marker_size, y + marker_size), fill=color, outline="black")

    if node.last_move is not None:
        r, c = node.last_move
        x = padding + c * cell_size
        y = padding + r * cell_size
        highlight_offset = stone_radius + 2
        drawer.rectangle((x - highlight_offset, y - highlight_offset, x + highlight_offset, y + highlight_offset), outline="red", width=2)

    indicator_radius = 4
    indicator_padding = 6
    indicator_x = img_size - indicator_padding
    indicator_y = indicator_padding
    indicator_color = "black" if node.turn == 1 else "white"
    drawer.ellipse((indicator_x - indicator_radius, indicator_y - indicator_radius, indicator_x + indicator_radius, indicator_y + indicator_radius), fill=indicator_color, outline="black")
    
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
    CSV_FILE_PATH = 'boar_yose-dame.csv'
    MAX_DEPTH = 3
    OUTPUT_IMAGE_PATH = 'game_tree_analysis'
    NODE_IMAGE_DIR = 'game_tree_nodes'

    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return
    
    os.makedirs(NODE_IMAGE_DIR, exist_ok=True)
    
    # --- 変更点(2): 2つの手番の分析に対応 ---
    # Graphvizのメイングラフを作成
    dot = graphviz.Digraph(comment='Go Game Tree Analysis')
    dot.attr(bgcolor='lightgray', rankdir='TB', label='Game Tree Analysis', fontsize='20')
    dot.attr('node', style='filled', fillcolor='white')

    # --- 黒先手の場合のサブグラフ ---
    with dot.subgraph(name='cluster_black', graph_attr={'label': 'Black to Play First', 'fontsize':'16', 'style':'filled', 'color':'whitesmoke'}) as sub_dot_black:
        start_node_black = GameState(board_data, turn=1)
        print("黒先手のゲーム木を構築中...")
        build_tree(start_node_black, MAX_DEPTH, set())
        print("黒先手のゲーム木を可視化中...")
        visualize_tree(start_node_black, sub_dot_black, NODE_IMAGE_DIR, set())

    # --- 白先手の場合のサブグラフ ---
    with dot.subgraph(name='cluster_white', graph_attr={'label': 'White to Play First', 'fontsize':'16', 'style':'filled', 'color':'lightgoldenrodyellow'}) as sub_dot_white:
        start_node_white = GameState(board_data, turn=-1)
        print("白先手のゲーム木を構築中...")
        build_tree(start_node_white, MAX_DEPTH, set())
        print("白先手のゲーム木を可視化中...")
        visualize_tree(start_node_white, sub_dot_white, NODE_IMAGE_DIR, set())
    
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

