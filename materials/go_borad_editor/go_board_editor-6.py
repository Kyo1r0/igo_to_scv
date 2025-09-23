import tkinter as tk
from tkinter import filedialog
import csv

# Pillow(PIL)ライブラリのインポート
try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    print("エラー: Pillowライブラリが見つかりません。")
    print("コマンドプロンプトで pip install Pillow を実行してください。")
    exit()

class GoBoardApp:
    def __init__(self, root, size):
        self.root = root
        self.size = size
        self.padding = 30
        self.cell_size = 40
        self.stone_radius = 18
        # ユーザーが編集するのは常に 1, -1, 0 のみの盤面
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]

        self.root.title(f"囲碁局面エディタ ({self.size}x{self.size})")
        
        canvas_total_size = self.cell_size * (self.size - 1) + 2 * self.padding

        self.board_image = Image.new("RGB", (canvas_total_size, canvas_total_size), "#D1B48C")
        self.drawer = ImageDraw.Draw(self.board_image)
        self.photo_image = None

        # --- GUIコンポーネント ---
        self.stone_color_var = tk.IntVar(value=1)
        
        # --- 変更点(1): ラジオボタンを簡略化 ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        tk.Radiobutton(control_frame, text="黒石", variable=self.stone_color_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="白石", variable=self.stone_color_var, value=-1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="消去", variable=self.stone_color_var, value=0).pack(side=tk.LEFT)
        
        self.canvas = tk.Canvas(self.root, width=canvas_total_size, height=canvas_total_size)
        self.canvas.pack()

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="CSVに保存", command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="PNG画像として保存", command=self.save_to_png).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="盤面をクリア", command=self.clear_board).pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def draw_board(self):
        """メモリ上の画像に盤面と石を描画し、キャンバスに表示する"""
        self.drawer.rectangle([0, 0, self.board_image.width, self.board_image.height], fill="#D1B48C")

        start = self.padding
        end = self.cell_size * (self.size - 1) + self.padding
        for i in range(self.size):
            pos = start + i * self.cell_size
            self.drawer.line([(start, pos), (end, pos)], fill="black")
            self.drawer.line([(pos, start), (pos, end)], fill="black")

        for r in range(self.size):
            for c in range(self.size):
                point_data = self.board_data[r][c]
                x = self.padding + c * self.cell_size
                y = self.padding + r * self.cell_size

                # --- 変更点(2): 石の描画のみに単純化 ---
                if point_data == 1 or point_data == -1:
                    color = "black" if point_data == 1 else "white"
                    bbox = (x - self.stone_radius, y - self.stone_radius, x + self.stone_radius, y + self.stone_radius)
                    self.drawer.ellipse(bbox, fill=color, outline="black")

        self.photo_image = ImageTk.PhotoImage(self.board_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def handle_click(self, event):
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)

        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        self.board_data[row][col] = self.stone_color_var.get()
        self.draw_board()

    # --- 変更点(3): 保存時に盤面を分析する新機能 ---
    def analyze_board_for_export(self):
        """
        現在の盤面を分析し、囲まれた空点を専用点(2, -2)に変換した
        エクスポート用の新しい盤面データを返す。
        """
        # 元のデータを変更しないようにディープコピーを作成
        export_data = [row[:] for row in self.board_data]
        
        for r in range(self.size):
            for c in range(self.size):
                if self.board_data[r][c] == 0: # 空点のみをチェック
                    neighbors = []
                    # 上下左右の隣接点をチェック
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        # 盤面の範囲内か確認
                        if 0 <= nr < self.size and 0 <= nc < self.size:
                            neighbor_stone = self.board_data[nr][nc]
                            # 隣が石であればリストに追加
                            if neighbor_stone == 1 or neighbor_stone == -1:
                                neighbors.append(neighbor_stone)
                    
                    # 隣接する石が1つ以上あり、かつ全て同じ色かチェック
                    if neighbors and all(s == 1 for s in neighbors):
                        export_data[r][c] = 2 # 黒の専用点に変換
                    elif neighbors and all(s == -1 for s in neighbors):
                        export_data[r][c] = -2 # 白の専用点に変換
        
        return export_data

    def save_to_csv(self):
        filename = filedialog.asksaveasfilename(
            title="CSVファイルとして保存", defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not filename: return
        
        # --- 変更点(4): 分析したデータを保存 ---
        export_data = self.analyze_board_for_export()
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(export_data)
            print(f"盤面を {filename} に保存しました。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")

    def save_to_png(self):
        filename = filedialog.asksaveasfilename(
            title="PNG画像として保存", defaultextension=".png", filetypes=[("PNG files", "*.png")]
        )
        if not filename: return
        try:
            self.board_image.save(filename)
            print(f"盤面画像を {filename} に保存しました。")
        except Exception as e:
            print(f"エラー: 画像の保存に失敗しました: {e}")
            
    def clear_board(self):
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.stone_color_var.set(1)
        self.draw_board()

class SizeSelectionDialog:
    def __init__(self, parent):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title("サイズ選択")
        self.selected_size = None
        tk.Label(self.top, text="碁盤のサイズを選択してください:", pady=10).pack()
        button_frame = tk.Frame(self.top)
        button_frame.pack(pady=10, padx=20)
        sizes = [6, 9, 11, 13, 19]
        for size in sizes:
            btn = tk.Button(button_frame, text=f"{size}x{size}", command=lambda s=size: self.select_size(s))
            btn.pack(side=tk.LEFT, padx=5)
        self.parent.withdraw()
        self.top.protocol("WM_DELETE_WINDOW", self.parent.destroy)

    def select_size(self, size):
        self.selected_size = size
        self.top.destroy()
        self.parent.deiconify()

if __name__ == "__main__":
    main_root = tk.Tk()
    dialog = SizeSelectionDialog(main_root)
    main_root.wait_window(dialog.top)
    if dialog.selected_size:
        app = GoBoardApp(main_root, size=dialog.selected_size)
        main_root.mainloop()
    else:
        print("サイズが選択されなかったので終了します。")

