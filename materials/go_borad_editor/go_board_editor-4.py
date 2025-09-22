import tkinter as tk
from tkinter import filedialog
import csv
import os

# Pillow(PIL)ライブラリのインポート
try:
    from PIL import Image, ImageGrab
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
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]

        self.root.title(f"囲碁局面エディタ ({self.size}x{self.size})")

        self.stone_color_var = tk.IntVar()
        self.stone_color_var.set(1)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        tk.Radiobutton(control_frame, text="黒を置く", variable=self.stone_color_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="白を置く", variable=self.stone_color_var, value=-1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="消去する", variable=self.stone_color_var, value=0).pack(side=tk.LEFT)
        
        canvas_size = self.cell_size * (self.size - 1) + 2 * self.padding
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size, bg='#D1B48C')
        self.canvas.pack()

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="CSVに保存", command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="PNG画像として保存", command=self.save_to_png).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="盤面をクリア", command=self.clear_board).pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def draw_board(self):
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
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)

        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        selected_stone = self.stone_color_var.get()
        self.board_data[row][col] = selected_stone
        self.draw_board()

    def save_to_csv(self):
        filename = filedialog.asksaveasfilename(
            title="CSVファイルとして保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename: return
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self.board_data)
            print(f"盤面を {filename} に保存しました。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")

    def save_to_png(self):
        """盤面をスクリーンショットで撮影してPNGファイルに保存する"""
        filename = filedialog.asksaveasfilename(
            title="PNG画像として保存",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        if not filename: return

        # ウィンドウの描画を強制的に更新
        self.root.update_idletasks()

        # キャンバスのスクリーン上の座標を取得
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # 座標を指定してスクリーンショットを撮影
        try:
            img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            img.save(filename, 'png')
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