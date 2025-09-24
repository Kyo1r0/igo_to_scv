import csv
import graphviz
import hashlib
import os
from PIL import Image, ImageDraw

EMPTY = 0
BLACK = 1
WHITE = -1

class GameState:
    """
    一つの囲碁の局面を管理するクラス。
    board: tuple of tuples
    turn: 1 = 黒, -1 = 白
    last_move: (r,c) or None
    parent: 親 GameState
    """
    def __init__(self, board_data, turn=1, last_move=None, parent=None):
        self.board = tuple(map(tuple, board_data))
        self.turn = turn
        self.size = len(self.board)
        self.last_move = last_move
        self.parent = parent
        self.id = self._generate_id()

    def _generate_id(self):
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        turn_str = str(self.turn)
        last_move_str = str(self.last_move)
        return hashlib.sha1((board_str + turn_str + last_move_str).encode()).hexdigest()[:10]

    def _tuple_board(self, board_list):
        return tuple(map(tuple, board_list))

    def _get_group_and_liberties(self, board_list, sr, sc):
        n = self.size
        color = board_list[sr][sc]
        if color == 0:
            return set(), set()
        stack = [(sr, sc)]
        group = set()
        liberties = set()
        visited = set()
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            group.add((r, c))
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n:
                    val = board_list[nr][nc]
                    if val == 0:
                        liberties.add((nr, nc))
                    elif val == color and (nr, nc) not in visited:
                        stack.append((nr, nc))
        return group, liberties

    def _is_same_board_as_ancestor(self, candidate_board_tuple):
        p = self
        while p is not None:
            if p.board == candidate_board_tuple:
                return True
            p = p.parent
        return False

    def generate_moves(self):
        moves = []
        player_color = self.turn
        n = self.size

        for r in range(n):
            for c in range(n):
                point = self.board[r][c]

                can_play = (point == 0) or \
                           (player_color == 1 and point == 2) or \
                           (player_color == -1 and point == -2)
                if not can_play:
                    continue

                new_board = [list(row) for row in self.board]
                new_board[r][c] = player_color

                opponent = -player_color
                captured_any = False
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n and new_board[nr][nc] == opponent:
                        group, libs = self._get_group_and_liberties(new_board, nr, nc)
                        if len(libs) == 0:
                            captured_any = True
                            for (gr, gc) in group:
                                new_board[gr][gc] = 0

                group_self, libs_self = self._get_group_and_liberties(new_board, r, c)
                if len(libs_self) == 0 and not captured_any:
                    continue

                candidate_board_tuple = self._tuple_board(new_board)
                if self._is_same_board_as_ancestor(candidate_board_tuple):
                    continue

                child_state = GameState(new_board, -player_color, last_move=(r, c), parent=self)
                moves.append(child_state)

        return moves

def create_node_image(node, file_path):
    """
    盤面だけ表示するPNG画像生成（右上インジケータなし、テキストなし）
    """
    padding = 5
    cell_size = 15
    stone_radius = 6
    img_size = cell_size * (node.size - 1) + 2 * padding

    image = Image.new("RGB", (img_size, img_size), "#D1B48C")
    drawer = ImageDraw.Draw(image)

    # 格子の描画
    start = padding
    end = cell_size * (node.size - 1) + padding
    for i in range(node.size):
        pos = start + i * cell_size
        drawer.line([(start, pos), (end, pos)], fill="black")
        drawer.line([(pos, start), (pos, end)], fill="black")

    # 石の描画
    for r in range(node.size):
        for c in range(node.size):
            point_data = node.board[r][c]
            x = padding + c * cell_size
            y = padding + r * cell_size

            if point_data == 1 or point_data == -1:
                color = "black" if point_data == 1 else "white"
                drawer.ellipse(
                    (x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius),
                    fill=color,
                    outline="black"
                )
            elif point_data == 2 or point_data == -2:
                color = "black" if point_data == 2 else "white"
                marker_size = 4
                drawer.rectangle(
                    (x - marker_size, y - marker_size, x + marker_size, y + marker_size),
                    fill=color,
                    outline="black"
                )

    # 直前手ハイライト
    if node.last_move is not None:
        r, c = node.last_move
        x = padding + c * cell_size
        y = padding + r * cell_size
        highlight_offset = stone_radius + 2
        drawer.rectangle(
            (x - highlight_offset, y - highlight_offset, x + highlight_offset, y + highlight_offset),
            outline="red", width=2
        )

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
    CSV_FILE_PATH = 'board_simple.csv'
    MAX_DEPTH = 3
    NODE_IMAGE_DIR = 'game_tree_nodes'

    try:
        with open(CSV_FILE_PATH, 'r') as f:
            reader = csv.reader(f)
            board_data = [[int(cell) for cell in row] for row in reader]
    except FileNotFoundError:
        print(f"エラー: {CSV_FILE_PATH} が見つかりません。")
        return

    os.makedirs(NODE_IMAGE_DIR, exist_ok=True)

    # 黒先手
    dot_black = graphviz.Digraph(comment='Black to Play First')
    dot_black.attr(bgcolor='lightgray', rankdir='TB')
    dot_black.attr('node', style='filled', fillcolor='white')
    start_node_black = GameState(board_data, turn=1)
    build_tree(start_node_black, MAX_DEPTH, set())
    visualize_tree(start_node_black, dot_black, NODE_IMAGE_DIR, set())
    dot_black.render('black_first', format='png', view=False, cleanup=True)

    # 白先手
    dot_white = graphviz.Digraph(comment='White to Play First')
    dot_white.attr(bgcolor='lightgray', rankdir='TB')
    dot_white.attr('node', style='filled', fillcolor='white')
    start_node_white = GameState(board_data, turn=-1)
    build_tree(start_node_white, MAX_DEPTH, set())
    visualize_tree(start_node_white, dot_white, NODE_IMAGE_DIR, set())
    dot_white.render('white_first', format='png', view=True, cleanup=True)

if __name__ == "__main__":
    main()
