import tkinter as tk
from tkinter import filedialog
import csv

class GoBoardApp:
    def __init__(self, root, size=9):
        # --- 基本設定 ---
        self.root = root
        self.size = size
        self.padding = 30
        self.cell_size = 40
        self.stone_radius = 18
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]
        # self.current_turn = 1 # --- 削除 ---: 自動切り替えは不要に

        self.root.title("囲碁局面エディタ")

        # --- GUIコンポーネントの作成 ---
        # --- 変更点(1): 色選択用の変数を追加 ---
        self.stone_color_var = tk.IntVar()
        self.stone_color_var.set(1) # 初期値は「黒」

        # ボタンとラジオボタン用のフレーム
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # --- 変更点(2): 色を選択するラジオボタンを作成 ---
        tk.Radiobutton(control_frame, text="黒を置く", variable=self.stone_color_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="白を置く", variable=self.stone_color_var, value=-1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="消去する", variable=self.stone_color_var, value=0).pack(side=tk.LEFT)
        
        # 盤面を描画するキャンバス
        canvas_size = self.cell_size * (self.size - 1) + 2 * self.padding
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size, bg='#D1B48C')
        self.canvas.pack()

        # 保存・クリアボタン用のフレーム
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        
        self.save_button = tk.Button(action_frame, text="CSVに保存", command=self.save_to_csv)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = tk.Button(action_frame, text="盤面をクリア", command=self.clear_board)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # --- イベントの設定 ---
        self.canvas.bind("<Button-1>", self.handle_click)

        # --- 初期描画 ---
        self.draw_board()

    def draw_board(self):
        """盤面と石を全て描画する"""
        self.canvas.delete("all")
        start = self.padding
        end = self.cell_size * (self.size - 1) + self.padding
        for i in range(self.size):
            pos = start + i * self.cell_size
            self.canvas.create_line(start, pos, end, pos)
            self.canvas.create_line(pos, start, pos, end)

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
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)

        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        # --- 変更点(3): ラジオボタンで選択された値をデータに設定 ---
        selected_stone = self.stone_color_var.get()
        self.board_data[row][col] = selected_stone

        # --- 削除 ---: 手番交代のロジックは不要
        # self.current_turn *= -1 
        
        self.draw_board()

    def save_to_csv(self):
        """盤面データをCSVファイルに保存する"""
        filename = filedialog.asksaveasfilename(
            title="CSVファイルとして保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return

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
        # --- 変更点(4): ラジオボタンの選択も初期化 ---
        self.stone_color_var.set(1)
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = GoBoardApp(root, size=9)
    root.mainloop()