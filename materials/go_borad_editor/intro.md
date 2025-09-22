```
import tkinter as tk
from tkinter import filedialog
import csv

# Pillow(PIL)ライブラリをインポートします。
# Image: 画像データそのものを扱うための基本クラスです。
# ImageDraw: 画像に線や円を描画するためのツールです。
# ImageTk: Pillowの画像をTkinterのウィンドウに表示できる形式に変換します。
try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    print("エラー: Pillowライブラリが見つかりません。")
    print("コマンドプロンプトで pip install Pillow を実行してください。")
    exit()

# ----------------------------------------------------------------------
# 3. メインの碁盤エディタアプリケーションのクラス
# ----------------------------------------------------------------------
class GoBoardApp:
    # --- 初期化メソッド ---
    # アプリケーションが起動したときに、最初に一度だけ実行されます。
    # ウィンドウの部品を作成し、変数を準備する役割があります。
    def __init__(self, root, size):
        self.root = root  # メインウィンドウ
        self.size = size  # 選択された盤面のサイズ (例: 9)

        # 描画に関する設定値
        self.padding = 30      # 盤の外側の余白
        self.cell_size = 40    # マス目（格子）のサイズ
        self.stone_radius = 18 # 石の半径

        # 盤面の状態を保持する2次元リスト (0: 空点, 1: 黒, -1: 白)
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]

        self.root.title(f"囲碁局面エディタ ({self.size}x{self.size})")
        
        # 描画領域全体のピクセルサイズを計算
        canvas_total_size = self.cell_size * (self.size - 1) + 2 * self.padding

        # --- 画像保存の仕組みの核心部分 ---
        # (1) Pillowを使って、メモリ上にまっさらな画像オブジェクトを作成します。
        #     これが私たちの「描画キャンバス本体」になります。
        self.board_image = Image.new("RGB", (canvas_total_size, canvas_total_size), "#D1B48C")
        # (2) 作成した画像に描画するための「ペン」を取得します。
        self.drawer = ImageDraw.Draw(self.board_image)
        # (3) メモリ上の画像をTkinterウィンドウに表示するための変数です。
        self.photo_image = None

        # --- GUI部品（ウィジェット）の配置 ---
        # ラジオボタンで選択された値 (1, -1, 0) を保持する変数
        self.stone_color_var = tk.IntVar(value=1)
        
        # ラジオボタンを配置するためのフレーム（容器）
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        tk.Radiobutton(control_frame, text="黒を置く", variable=self.stone_color_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="白を置く", variable=self.stone_color_var, value=-1).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="消去する", variable=self.stone_color_var, value=0).pack(side=tk.LEFT)
        
        # ユーザーに盤面を見せるためのTkinterのCanvasウィジェット
        self.canvas = tk.Canvas(self.root, width=canvas_total_size, height=canvas_total_size)
        self.canvas.pack()

        # ボタン類を配置するためのフレーム
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="CSVに保存", command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="PNG画像として保存", command=self.save_to_png).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="盤面をクリア", command=self.clear_board).pack(side=tk.LEFT, padx=5)

        # マウスクリック時の動作（handle_clickメソッド）をCanvasに設定
        self.canvas.bind("<Button-1>", self.handle_click)
        
        # 起動時に一度、盤面を描画する
        self.draw_board()

    # --- 描画メソッド ---
    def draw_board(self):
        """メモリ上の画像に盤面と石を描画し、その結果をキャンバスに表示する"""
        # メモリ上の画像を碁盤の色で塗りつぶして初期化
        self.drawer.rectangle([0, 0, self.board_image.width, self.board_image.height], fill="#D1B48C")

        # 格子線をメモリ上の画像に描画
        start = self.padding
        end = self.cell_size * (self.size - 1) + self.padding
        for i in range(self.size):
            pos = start + i * self.cell_size
            self.drawer.line([(start, pos), (end, pos)], fill="black") # 横線
            self.drawer.line([(pos, start), (pos, end)], fill="black") # 縦線

        # self.board_dataの内容に従って、石をメモリ上の画像に描画
        for r in range(self.size):
            for c in range(self.size):
                stone = self.board_data[r][c]
                if stone != 0:
                    x = self.padding + c * self.cell_size
                    y = self.padding + r * self.cell_size
                    color = "black" if stone == 1 else "white"
                    bbox = (x - self.stone_radius, y - self.stone_radius, x + self.stone_radius, y + self.stone_radius)
                    self.drawer.ellipse(bbox, fill=color, outline="black")

        # 完成したメモリ上の画像を、Tkinterで表示できる形式に変換
        self.photo_image = ImageTk.PhotoImage(self.board_image)
        # 変換した画像をCanvasウィジェットに表示
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    # --- クリック処理メソッド ---
    def handle_click(self, event):
        """盤面がクリックされたときに実行される"""
        # クリックされたピクセル座標を、盤上の(行, 列)のインデックスに変換
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)

        # 盤面の範囲外なら何もしない
        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        # 盤面データ(2次元リスト)を更新
        self.board_data[row][col] = self.stone_color_var.get()
        # 盤面を再描画して変更を画面に反映
        self.draw_board()

    # --- CSV保存メソッド ---
    def save_to_csv(self):
        # 保存ダイアログを開き、ユーザーにファイル名を入力させる
        filename = filedialog.asksaveasfilename(
            title="CSVファイルとして保存", defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not filename: return # キャンセルされたら何もしない
        try:
            # 指定されたファイルに盤面データ(2次元リスト)を書き込む
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self.board_data)
            print(f"盤面を {filename} に保存しました。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")

    # --- PNG保存メソッド ---
    def save_to_png(self):
        """メモリ上の画像を直接PNGファイルに保存する"""
        filename = filedialog.asksaveasfilename(
            title="PNG画像として保存", defaultextension=".png", filetypes=[("PNG files", "*.png")]
        )
        if not filename: return
        try:
            # メモリ上に保持しているPillowの画像オブジェクトを直接保存
            self.board_image.save(filename)
            print(f"盤面画像を {filename} に保存しました。")
        except Exception as e:
            print(f"エラー: 画像の保存に失敗しました: {e}")
            
    # --- クリアメソッド ---
    def clear_board(self):
        # 盤面データをすべて0に戻す
        self.board_data = [[0 for _ in range(self.size)] for _ in range(self.size)]
        # ラジオボタンの選択を「黒を置く」に戻す
        self.stone_color_var.set(1)
        # 盤面を再描画
        self.draw_board()

# ----------------------------------------------------------------------
# 2. 起動時に表示されるサイズ選択ウィンドウのクラス
# ----------------------------------------------------------------------
class SizeSelectionDialog:
    def __init__(self, parent):
        self.parent = parent
        # Toplevelでメインウィンドウとは別の新しいウィンドウを作成
        self.top = tk.Toplevel(parent)
        self.top.title("サイズ選択")
        self.selected_size = None # ユーザーが選択したサイズを保持する変数

        tk.Label(self.top, text="碁盤のサイズを選択してください:", pady=10).pack()

        button_frame = tk.Frame(self.top)
        button_frame.pack(pady=10, padx=20)
        
        sizes = [6, 9, 11, 13, 19]
        for size in sizes:
            # commandのlambda式は、ボタンが押された瞬間に正しいsizeの値を渡すための工夫
            btn = tk.Button(button_frame, text=f"{size}x{size}", command=lambda s=size: self.select_size(s))
            btn.pack(side=tk.LEFT, padx=5)

        # ユーザーが選択するまで、裏にあるメインウィンドウを隠す
        self.parent.withdraw()
        # 選択ウィンドウが閉じられたらプログラム全体を終了する
        self.top.protocol("WM_DELETE_WINDOW", self.parent.destroy)

    def select_size(self, size):
        """サイズボタンが押されたときに実行される"""
        self.selected_size = size
        self.top.destroy() # 選択ウィンドウを閉じる
        self.parent.deiconify() # 隠していたメインウィンドウを再表示する

# ----------------------------------------------------------------------
# 1. プログラムの実行開始点
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # まずはメインウィンドウの器を作成する
    main_root = tk.Tk()
    
    # サイズ選択ダイアログを開く
    dialog = SizeSelectionDialog(main_root)
    # ユーザーがダイアログを操作し終えるまで、ここで待機する
    main_root.wait_window(dialog.top)

    # ダイアログでサイズが正常に選択された場合
    if dialog.selected_size:
        # 選択されたサイズを使って、メインのアプリを起動する
        app = GoBoardApp(main_root, size=dialog.selected_size)
        # ウィンドウのイベントループを開始（ウィンドウが表示され、操作可能になる）
        main_root.mainloop()
    else:
        # サイズが選択されずにダイアログが閉じられた場合
        print("サイズが選択されなかったので終了します。")

```