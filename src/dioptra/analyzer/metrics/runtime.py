from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext, Plaintext
from dioptra.analyzer.metrics.multdepth import MultDepth
from inspect import Traceback
import dis

class Runtime(AnalysisBase):
    total_runtime : int
    instruction_num: int
    multiplicative_depth: MultDepth
    runtime_table : dict[(str, int), int]
    where : dict[int, tuple[int, str, dis.Positions]]
    unit: str

    def __init__(self, multiplicative_depth: MultDepth, runtime_table: dict[str, int]) -> None:
        self.total_runtime = 0
        self.multiplicative_depth = multiplicative_depth
        self.runtime_table = runtime_table
        self.where = {}
        self.unit = "sec"
        

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("mult_ctct", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_mul_ctpt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Plaintext, call_loc: Traceback) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("mult_ctpt", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("add_ctct", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Plaintext, call_loc: Traceback) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("add_ctpt", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("sub_ctct", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_sub_ctpt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Plaintext, call_loc: Traceback) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("sub_ctpt", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_bootstrap(self, dest: Ciphertext, ct1: Ciphertext, call_loc: Traceback | None) -> None:
        (mult_depth, _, _) = self.multiplicative_depth.where[dest]
        self.total_runtime += self.runtime_table[("bootstrap", mult_depth)]
        self.set_runtime(dest, self.total_runtime, call_loc)

    def set_runtime(self, ct: Ciphertext, runtime: int, call_loc: Traceback) -> None:
        self.where[ct] = (runtime, call_loc.filename, call_loc.positions) # type: ignore
    