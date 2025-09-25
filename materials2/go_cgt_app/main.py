import argparse
import csv
from gui.board_editor import launch_board_editor
from logic.game_state import GameState
from logic.tree_builder import build_tree, visualize_tree
from logic.evaluator import evaluate

def load_board_from_csv(path):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        return [[int(cell) for cell in row] for row in reader]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["gui", "tree", "eval"], default="gui")
    parser.add_argument("--file", help="CSV file for board")
    args = parser.parse_args()

    if args.mode == "gui":
        launch_board_editor()
    elif args.mode == "tree":
        if not args.file:
            print("Please provide --file CSV")
            return
        board = load_board_from_csv(args.file)
        state = GameState(board)
        tree = build_tree(state, depth=2)
        visualize_tree(tree)
    elif args.mode == "eval":
        if not args.file:
            print("Please provide --file CSV")
            return
        board = load_board_from_csv(args.file)
        state = GameState(board)
        val = evaluate(state)
        print("Game value =", val)

if __name__ == "__main__":
    main()
