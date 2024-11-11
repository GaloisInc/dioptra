import dis

from dioptra.pke.analysisbase import (
    AnalysisBase,
    Ciphertext,
    Plaintext,
    PublicKey,
)
from dioptra.pke.calibration import Event, EventKind, PKECalibrationData
from dioptra.report.runtime import RuntimeReport
from dioptra.utils.code_loc import Frame
from dioptra.utils.network import NetworkModel


class Runtime(AnalysisBase):
    def __init__(
        self, runtime_samples: PKECalibrationData, report: RuntimeReport
    ) -> None:
        self.runtime_table = runtime_samples.avg_runtime_table()
        self.where: dict[dis.Positions, int] = {}
        self.ct_size = runtime_samples.ct_mem
        self.report = report

    def report_event(self, event: Event, call_loc: Frame | None):
        self.report.runtime_estimate(call_loc, self.runtime_table.get_runtime_ns(event))

    def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame) -> None:
        self.report_event(Event(EventKind.ENCODE, dest.level), call_loc)

    def trace_encode_ckks(self, dest: Plaintext, call_loc: Frame) -> None:
        self.report_event(Event(EventKind.ENCODE, dest.level), call_loc)

    def trace_encrypt(
        self,
        dest: Ciphertext,
        publicKey: PublicKey,
        plaintext: Plaintext,
        call_loc: Frame,
    ) -> None:
        self.report_event(Event(EventKind.ENCRYPT, plaintext.level), call_loc)

    def trace_decrypt(
        self,
        dest: Plaintext,
        publicKey: PublicKey,
        ciphertext: Ciphertext,
        call_loc: Frame,
    ) -> None:
        self.report_event(Event(EventKind.DECRYPT, ciphertext.level), call_loc)

    def trace_mul_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame
    ) -> None:
        self.report_event(
            Event(EventKind.EVAL_MULT_CTCT, ct1.level, ct2.level), call_loc
        )

    def trace_add_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame
    ) -> None:
        self.report_event(
            Event(EventKind.EVAL_ADD_CTCT, ct1.level, ct2.level), call_loc
        )

    def trace_sub_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame
    ) -> None:
        self.report_event(
            Event(EventKind.EVAL_SUB_CTCT, ct1.level, ct2.level), call_loc
        )

    def trace_mul_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        self.report_event(Event(EventKind.EVAL_MULT_CTPT, ct.level, pt.level), call_loc)

    def trace_add_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        self.report_event(Event(EventKind.EVAL_ADD_CTPT, ct.level, pt.level), call_loc)

    def trace_sub_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        self.report_event(Event(EventKind.EVAL_SUB_CTPT, ct.level, pt.level), call_loc)

    def trace_bootstrap(
        self, dest: Ciphertext, ct: Ciphertext, call_loc: Frame | None
    ) -> None:
        self.report_event(Event(EventKind.EVAL_BOOTSTRAP), call_loc)

    def trace_send_ct(
        self, ct: Ciphertext, nm: NetworkModel, call_loc: Frame | None
    ) -> None:
        runtime = nm.send_latency_ns(self.ct_size[ct.level.level])
        self.report.runtime_estimate(call_loc, runtime)

    def trace_recv_ct(
        self, ct: Ciphertext, nm: NetworkModel, call_loc: Frame | None
    ) -> None:
        runtime = nm.recv_latency_ns(self.ct_size[ct.level.level])
        self.report.runtime_estimate(call_loc, runtime)
