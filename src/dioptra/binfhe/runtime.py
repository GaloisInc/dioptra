import openfhe

from dioptra.binfhe.analyzer import BinFHEAnalysisBase
from dioptra.binfhe.event import BinFHEEvent, BinFHEEventKind
from dioptra.binfhe.value import LWECiphertext, LWEPrivateKey
from dioptra.report.runtime import RuntimeReport
from dioptra.utils.code_loc import Frame
from dioptra.utils.network import NetworkModel


class RuntimeEstimate(BinFHEAnalysisBase):
    def __init__(
        self, ort: dict[BinFHEEvent, int], ct_size: int, report: RuntimeReport
    ):
        self.operation_runtime_table = ort
        self.runtime_report = report
        self.ct_size = ct_size

    def trace_evt(self, evt: BinFHEEvent, loc: Frame | None):
        runtime = self.operation_runtime_table[evt]
        self.runtime_report.runtime_estimate(loc, runtime)

    def trace_encrypt(self, dest: LWECiphertext, sk: LWEPrivateKey, loc: Frame | None):
        self.trace_evt(BinFHEEvent(BinFHEEventKind.ENCRYPT), loc)

    def trace_decrypt(self, sk: LWEPrivateKey, ct: LWECiphertext, loc: Frame | None):
        self.trace_evt(BinFHEEvent(BinFHEEventKind.DECRYPT), loc)

    def trace_keygen(self, key: LWEPrivateKey, loc: Frame | None):
        self.trace_evt(BinFHEEvent(BinFHEEventKind.KEYGEN), loc)

    def trace_eval_gate(
        self,
        gate: openfhe.BINGATE,
        dest: LWECiphertext,
        c1: LWECiphertext,
        c2: LWECiphertext,
        loc: Frame | None,
    ):
        evt = BinFHEEvent.bingate_to_event().get(gate, None)
        if evt is None:
            raise NotImplementedError(
                f"Gate not implemented in runtime analysis {gate.name}"
            )

        self.trace_evt(evt, loc)

    def trace_eval_not(self, dest: LWECiphertext, c: LWECiphertext, loc: Frame | None):
        self.trace_evt(BinFHEEvent(BinFHEEventKind.EVAL_NOT), loc)

    def trace_send_ct(
        self, ct: LWECiphertext, nm: NetworkModel, loc: Frame | None
    ) -> None:
        runtime = nm.send_latency_ns(self.ct_size)
        self.runtime_report.runtime_estimate(loc, runtime)

    def trace_recv_ct(
        self, ct: LWECiphertext, nm: NetworkModel, loc: Frame | None
    ) -> None:
        runtime = nm.recv_latency_ns(self.ct_size)
        self.runtime_report.runtime_estimate(loc, runtime)
