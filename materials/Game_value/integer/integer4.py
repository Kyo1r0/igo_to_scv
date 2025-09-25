# --- 盤面画像を保存する関数 ---
from PIL import Image, ImageDraw
import csv
import hashlib
import os
from PIL import Image, ImageDraw

class GameValue:
    def __init__(self, value_type='UNKNOWN', value=None):
        self.type = value_type
        self.value = value
    def __repr__(self):
        if self.type == 'INTEGER':
            return str(self.value)
        return '?'


class GameState:
    def __init__(self, board_data):
        self.board = tuple(map(tuple, board_data))
        self.size = len(self.board)
        self.id = self._generate_id()

    def _generate_id(self):
        board_str = "".join(map(str, [item for row in self.board for item in row]))
        return hashlib.sha1(board_str.encode()).hexdigest()[:10]

    def generate_moves_for_player(self, player_color):
        moves = []
        allowed_empty_points = [0, player_color * 2]
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] in allowed_empty_points:
                    new_board_list = [list(row) for row in self.board]
                    new_board_list[r][c] = player_color
                    moves.append(GameState(new_board_list))
        return moves


# --- 値計算ロジック ---
memoization_cache = {}

def calculate_value(node):
    if node.id in memoization_cache:
        return memoization_cache[node.id]

    left_options = node.generate_moves_for_player(1)
    right_options = node.generate_moves_for_player(-1)
    
    left_values = {calculate_value(child) for child in left_options}
    right_values = {calculate_value(child) for child in right_options}

    if not left_options and not right_options:
        result = GameValue('INTEGER', 0)
        memoization_cache[node.id] = result
        return result

    all_children_are_integers = all(v.type == 'INTEGER' for v in left_values | right_values)

    if all_children_are_integers:
        if len(left_values) == 1 and not right_values:
            child_value = list(left_values)[0].value
            result = GameValue('INTEGER', child_value + 1)
            memoization_cache[node.id] = result
            return result
            
        if not left_values and len(right_values) == 1:
            child_value = list(right_values)[0].value
            result = GameValue('INTEGER', child_value - 1)
            memoization_cache[node.id] = result
            return result

    result = GameValue('UNKNOWN')
    memoization_cache[node.id] = result
    return result


# --- 盤面描画関数 (Pillow) ---
def draw_board_image(board_data, filename):
    size = len(board_data)
    padding = 30
    cell_size = 40
    stone_radius = 18
    canvas_total_size = cell_size * (size - 1) + 2 * padding

    img = Image.new("RGB", (canvas_total_size, canvas_total_size), "#D1B48C")
    draw = ImageDraw.Draw(img)

    # 線
    start = padding
    end = cell_size * (size - 1) + padding
    for i in range(size):
        pos = start + i * cell_size
        draw.line([(start, pos), (end, pos)], fill="black")
        draw.line([(pos, start), (pos, end)], fill="black")

    # 石/専用点
    for r in range(size):
        for c in range(size):
            point = board_data[r][c]
            x = padding + c * cell_size
            y = padding + r * cell_size

            if point == 1 or point == -1:  # 黒石/白石
                color = "black" if point == 1 else "white"
                bbox = (x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius)
                draw.ellipse(bbox, fill=color, outline="black")

            elif point == 2 or point == -2:  # 専用点
                marker_size = 6
                color = "black" if point == 2 else "white"
                bbox = (x - marker_size, y - marker_size, x + marker_size, y + marker_size)
                draw.rectangle(bbox, fill=color, outline="black")

    img.save(filename)


# --- 値と盤面を出力 ---
def dump_game_values(node, max_depth, f, depth=0, visited=None, outdir="output_images"):
    if visited is None:
        visited = set()
    if node.id in visited or depth > max_depth:
        return
    visited.add(node.id)

    value = calculate_value(node)
    f.write(f"Depth {depth}, ID {node.id}, Value: {value}\n")

    # 盤面画像を保存
    os.makedirs(outdir, exist_ok=True)
    img_path = os.path.join(outdir, f"{node.id}_d{depth}.png")
    draw_board_image(node.board, img_path)

    for child in node.generate_moves_for_player(1):
        dump_game_values(child, max_depth, f, depth+1, visited, outdir)
    for child in node.generate_moves_for_player(-1):
        dump_game_values(child, max_depth, f, depth+1, visited, outdir)


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

    base_name = os.path.splitext(CSV_FILE_PATH)[0]
    OUTPUT_FILE_PATH = f"{base_name}_value.txt"

    print("ゲーム木を構築し、値と画像を保存中...")
    with open(OUTPUT_FILE_PATH, "w") as f:
        dump_game_values(start_node, MAX_DEPTH, f)
    print(f"計算完了。値は {OUTPUT_FILE_PATH}、画像は output_images フォルダに保存しました。")


if __name__ == "__main__":
    main()

def save_board_as_png(board_data, filename):
    size = len(board_data)
    padding = 30
    cell_size = 40
    stone_radius = 18

    canvas_total_size = cell_size * (size - 1) + 2 * padding
    board_image = Image.new("RGB", (canvas_total_size, canvas_total_size), "#D1B48C")
    drawer = ImageDraw.Draw(board_image)

    # 碁盤の線を描画
    start = padding
    end = cell_size * (size - 1) + padding
    for i in range(size):
        pos = start + i * cell_size
        drawer.line([(start, pos), (end, pos)], fill="black")
        drawer.line([(pos, start), (pos, end)], fill="black")

    # 石の描画
    for r in range(size):
        for c in range(size):
            point_data = board_data[r][c]
            x = padding + c * cell_size
            y = padding + r * cell_size

            if point_data == 1 or point_data == -1:  # 石
                color = "black" if point_data == 1 else "white"
                bbox = (x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius)
                drawer.ellipse(bbox, fill=color, outline="black")
            elif point_data == 2 or point_data == -2:  # 専用点
                marker_size = 6
                color = "black" if point_data == 2 else "white"
                bbox = (x - marker_size, y - marker_size, x + marker_size, y + marker_size)
                drawer.rectangle(bbox, fill=color, outline="black")

    board_image.save(filename)
    print(f"盤面画像を {filename} に保存しました。")
    PNG_FILE_PATH = f"{base_name}.png"
    save_board_as_png(board_data, PNG_FILE_PATH)