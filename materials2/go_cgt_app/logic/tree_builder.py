import graphviz
from .game_state import GameState

def build_tree(state, depth=2):
    """
    再帰的にゲーム木を構築 (depth制限あり)
    """
    if depth == 0:
        return {}
    tree = {}
    for move in state.get_legal_moves():
        child = state.play_move(move)
        tree[move] = build_tree(child, depth-1)
    return tree

def visualize_tree(tree, filename="assets/game_tree"):
    dot = graphviz.Digraph()
    node_id = 0

    def add_node(subtree, parent=None):
        nonlocal node_id
        this_id = str(node_id)
        dot.node(this_id, label=f"Node {this_id}")
        node_id += 1
        if parent is not None:
            dot.edge(parent, this_id)
        for move, child in subtree.items():
            add_node(child, this_id)

    add_node(tree)
    dot.render(filename, format="png", cleanup=True)
    print(f"Tree saved to {filename}.png")
