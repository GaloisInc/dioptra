class BinFHEParams:
    def __init__(self, n: int, q: int, beta: int) -> None:
        self.n = n
        self.q = q
        self.beta = beta

    def to_dict(self):
        return {"n": self.n, "q": self.q, "beta": self.beta}

    @staticmethod
    def from_dict(d):
        return BinFHEParams(d["n"], d["q"], d["beta"])
