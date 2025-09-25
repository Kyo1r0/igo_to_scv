# 使い方

盤面エディタを起動

python main.py --mode gui


→ Tkinter GUI が立ち上がる。
→ 盤面を作って CSV 保存。

ゲーム木を構築 & 可視化

python main.py --mode tree --file board.csv


→ assets/game_tree.png に保存。

ゲーム値を計算

python main.py --mode eval --file board.csv


→ コンソールに Game value = ... と表示。