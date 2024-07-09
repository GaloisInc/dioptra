from analysis_base import AnalysisBase, Ciphertext
from inspect import Traceback


class Runtime(AnalysisBase):
    total_runtime : int
    runtime_table : dict[str, int]

    def __init__(self, runtime_table: dict[str, int]) -> None:
        self.total_runtime = 0
        self.runtime_table = runtime_table

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, where: Traceback) -> None:
        self.total_runtime += self.runtime_table["mult_ctct"]
        pass
    