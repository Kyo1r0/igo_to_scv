import tkinter as tk
from tkinter import filedialog
import csv

class GoBoardApp:
    def __init__(self, root, size=9):
        # --- 基本設定 ---
        self.root = root
        self.size = size
        self.padding = 30  # 盤の余白
        self.cell_size = 40  # マス目のサイズ
        self.stone_radius = 18 # 石の半径
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_turn = 1  # 1: 黒, -1: 白

        self.root.title("囲碁局面エディタ")

        # --- GUIコンポーネントの作成 ---
        # 盤面を描画するキャンバス
        canvas_size = self.cell_size * (self.size - 1) + 2 * self.padding
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size, bg='#D1B48C')
        self.canvas.pack()

        # ボタン用のフレーム
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # 保存ボタン
        self.save_button = tk.Button(button_frame, text="CSVに保存", command=self.save_to_csv)
        self.save_button.pack(side=tk.LEFT, padx=10)

        # クリアボタン
        self.clear_button = tk.Button(button_frame, text="盤面をクリア", command=self.clear_board)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # --- イベントの設定 ---
        self.canvas.bind("<Button-1>", self.handle_click)

        # --- 初期描画 ---
        self.draw_board()

    def draw_board(self):
        """盤面と石を全て描画する"""
        self.canvas.delete("all") # 描画内容を一旦全て消去

        # 格子線の描画
        start = self.padding
        end = self.cell_size * (self.size - 1) + self.padding
        for i in range(self.size):
            pos = start + i * self.cell_size
            self.canvas.create_line(start, pos, end, pos)  # 横線
            self.canvas.create_line(pos, start, pos, end)  # 縦線

        # 石の描画
        for r in range(self.size):
            for c in range(self.size):
                stone = self.board_data[r][c]
                if stone != 0:
                    x = self.padding + c * self.cell_size
                    y = self.padding + r * self.cell_size
                    color = "black" if stone == 1 else "white"
                    self.canvas.create_oval(
                        x - self.stone_radius, y - self.stone_radius,
                        x + self.stone_radius, y + self.stone_radius,
                        fill=color, outline=color
                    )

    def handle_click(self, event):
        """キャンバスがクリックされたときの処理"""
        # ピクセル座標をグリッドのインデックスに変換
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)

        # 盤面の範囲外は無視
        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        # 既に石が置かれている場合は無視
        if self.board_data[row][col] != 0:
            return

        # データを更新
        self.board_data[row][col] = self.current_turn
        
        # 手番を交代
        self.current_turn *= -1
        
        # 盤面を再描画
        self.draw_board()

    def save_to_csv(self):
        """盤面データをCSVファイルに保存する"""
        filename = filedialog.asksaveasfilename(
            title="CSVファイルとして保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return # キャンセルされた場合

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self.board_data)
            print(f"盤面を {filename} に保存しました。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            
    def clear_board(self):
        """盤面を初期状態に戻す"""
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_turn = 1
        self.draw_board()


if __name__ == "__main__":
    root = tk.Tk()
    app = GoBoardApp(root, size=9) # sizeを変更すれば路盤の大きさが変わります
    root.mainloop()