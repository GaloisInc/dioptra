from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext
from dioptra.analyzer.metrics.multdepth import MultDepth
from inspect import Traceback


class Runtime(AnalysisBase):
    total_runtime : int
    runtime_table : dict[(str, int), int]
    multiplicative_depth: MultDepth
    instruction_num: int

    def __init__(self, multiplicative_depth: MultDepth, runtime_table: dict[str, int]) -> None:
        self.instruction_num = 0
        self.total_runtime = 0
        self.runtime_table = runtime_table
        self.multiplicative_depth = multiplicative_depth

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, where: Traceback) -> None:
        self.instruction_num += 1
        (mult_depth, _, _) = self.multiplicative_depth.where[self.instruction_num]
        self.total_runtime += self.runtime_table[("mult_ctct", mult_depth)]
        pass
    