from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext, Plaintext
import dis
from inspect import Traceback

class MultDepth(AnalysisBase):
    depth : dict[Ciphertext, int]
    max_depth : int
    where : dict[int, tuple[int, str, dis.Positions]]
    unit: str
    instruction_num: int

    def __init__(self) -> None:
        self.depth = {}
        self.max_depth = 0
        self.where = {}
        self.unit = ""

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth, call_loc)    

    def trace_mul_ctpt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Plaintext, call_loc: Traceback) -> None:
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth, call_loc)

    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_add_ctpt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Plaintext, call_loc: Traceback) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_sub_ctpt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Plaintext, call_loc: Traceback) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_bootstrap(self, dest: Ciphertext, ct1: Ciphertext, call_loc: Traceback | None) -> None:
        new_depth = 0
        self.set_depth(dest, new_depth, call_loc)
    
    def depth_of(self, ct: Ciphertext) -> int:
        if ct in self.depth:
            return self.depth[ct]   
        return 0
    
    def set_depth(self, ct: Ciphertext, depth: int, call_loc: Traceback) -> None:
        self.depth[ct] = depth

        self.where[ct] = (depth, call_loc.filename, call_loc.positions) # type: ignore
        self.max_depth = max(depth, self.max_depth)