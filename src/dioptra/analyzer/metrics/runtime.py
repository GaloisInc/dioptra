from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext, Plaintext, PublicKey, PrivateKey
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.calibration import CalibrationData, Event, EventKind
from dioptra.analyzer.utils.code_loc import Frame
from dioptra.analyzer.utils.util import format_ns
import dis

class Runtime(AnalysisBase):

    def __init__(self, runtime_samples: CalibrationData) -> None:
        self.total_runtime = 0
        self.runtime_table = runtime_samples.avg_runtime_table()
        self.where = {}

    def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame) -> None:
        pass

    def trace_encode_ckks(self, dest: Plaintext, value: list[float], call_loc: Frame, level: int = 0)  -> None:
        dest_depth = level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.ENCODE, dest_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)  

    def trace_encrypt(self, dest: Ciphertext, publicKey: PublicKey, plaintext: Plaintext, call_loc: Frame) -> None:
        dest_depth = plaintext.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.ENCRYPT, dest_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)  
        
    def trace_decrypt(self, dest: Plaintext, publicKey: PublicKey, ciphertext: Ciphertext, call_loc: Frame) -> None:
        ct_depth = ciphertext.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.DECRYPT, ct_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)  

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = ct1.level
        ct2_depth = ct2.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_MULT_CTCT, ct1_depth, ct2_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)    

    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = ct1.level
        ct2_depth = ct2.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_ADD_CTCT, ct1_depth, ct2_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)
 
    def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame) -> None:
        ct1_depth = ct1.level
        ct2_depth = ct2.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_SUB_CTCT, ct1_depth, ct2_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)

    def trace_mul_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame| None) -> None:
        ct_depth = ct.level
        pt_depth = pt.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_MULT_CTPT, ct_depth, pt_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)
        
    def trace_add_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame| None) -> None:
        ct_depth = ct.level
        pt_depth = pt.level
        
        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_ADD_CTPT, ct_depth, pt_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)

    def trace_sub_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame| None) -> None:
        ct_depth = ct.level
        pt_depth = pt.level

        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_SUB_CTPT, ct_depth, pt_depth))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)

    def trace_bootstrap(self, dest: Ciphertext, ct: Ciphertext, call_loc: Frame | None) -> None:
        line_runtime = self.runtime_table.get_runtime_ns(Event(EventKind.EVAL_BOOTSTRAP))
        self.total_runtime += line_runtime
        self.set_runtime(dest, line_runtime, call_loc)

    def set_runtime(self, ct: Ciphertext, line_runtime: int, call_loc: Frame) -> None:
        while call_loc is not None:
            (file_name, positions) = call_loc.location()
            runtime = 0
            if positions in self.where.keys():
                (runtime, _, file_name, positions) = self.where[positions]

            runtime += line_runtime
            self.where[positions] = (runtime, format_ns(int(runtime)), file_name, positions)     
            call_loc = call_loc.caller()