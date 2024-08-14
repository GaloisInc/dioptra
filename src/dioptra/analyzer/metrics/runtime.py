from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext, Plaintext, PublicKey, PrivateKey
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.calibration import RuntimeTable, RuntimeSamples, Event, EventKind
from dioptra.analyzer.utils.code_loc import Frame
import dis

class Runtime(AnalysisBase):

    def __init__(self, multiplicative_depth: MultDepth, runtime_samples: RuntimeSamples) -> None:
        self.total_runtime = 0
        self.level = multiplicative_depth
        self.multiplicative_depth = multiplicative_depth
        self.runtime_table = runtime_samples.avg_runtime_table()
        self.where = {}
        self.unit = "nanosec"

    def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame) -> None:
        dest_depth = level
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.ENCODE, dest_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_encode_ckks(self, dest: Plaintext, value: list[float], call_loc: Frame, level: int = 0)  -> None:
        dest_depth = level
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.ENCODE, dest_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_encrypt(self, dest: Ciphertext, publicKey: PublicKey, plaintext: Plaintext, call_loc: Frame) -> None:
        dest_depth = plaintext.level
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.ENCRYPT, dest_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_decrypt(self, dest: Plaintext, publicKey: PublicKey, ciphertext: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = self.multiplicative_depth.depth[ciphertext]
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.DECRYPT, ct1_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = self.multiplicative_depth.depth[ct1]
        ct2_depth = self.multiplicative_depth.depth[ct2]
        
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_MULT, ct1_depth, ct2_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = self.multiplicative_depth.depth[ct1]
        ct2_depth = self.multiplicative_depth.depth[ct2]
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_ADD, ct1_depth, ct2_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = self.multiplicative_depth.depth[ct1]
        ct2_depth = self.multiplicative_depth.depth[ct2]
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_SUB, ct1_depth, ct2_depth))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def trace_bootstrap(self, dest: Ciphertext, ct1: Ciphertext, call_loc: Frame | None) -> None:
        self.total_runtime += self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_BOOTSTRAP))
        self.set_runtime(dest, self.total_runtime, call_loc)

    def set_runtime(self, ct: Ciphertext, runtime: int, call_loc: Frame) -> None:
        while call_loc is not None:
            (file_name, positions) = call_loc.location()
            self.where[positions] = (runtime, file_name, positions)
            call_loc = call_loc.caller()