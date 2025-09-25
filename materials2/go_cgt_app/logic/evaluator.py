from fractions import Fraction

class CGTValue:
    def __init__(self, base=0, star=False, up=False, down=False):
        if isinstance(base, int):
            self.base = Fraction(base, 1)
        elif isinstance(base, Fraction):
            self.base = base
        else:
            raise ValueError("base must be int or Fraction")
        self.star = star
        self.up = up
        self.down = down

    def __repr__(self):
        s = str(self.base)
        if self.star: s += "*"
        if self.up: s += "↑"
        if self.down: s += "↓"
        return s

def evaluate(state):
    """
    ダミー評価関数
    空点数 = 値
    """
    empty = sum(row.count(0) for row in state.board)
    return CGTValue(base=empty)
