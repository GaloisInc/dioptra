from dioptra.binfhe.analyzer import BinFHEAnalysisBase
from dioptra.binfhe.value import LWECiphertext
from dioptra.report.memory import AllocationType, MemoryReport
from dioptra.utils.code_loc import Frame


class BinFHEMemoryEstimate(BinFHEAnalysisBase):
    def __init__(self, setup_size: int, ct_size: int, report: MemoryReport):
        report.record_setup_size(setup_size)
        self.report = report
        self.ct_size = ct_size

    def trace_alloc_ct(self, dest: LWECiphertext, loc: Frame | None) -> None:
        self.report.record_alloc(AllocationType.CIPHERTEXT, dest.id, self.ct_size, loc)

    def trace_dealloc_ct(self, vid: int, loc: Frame | None) -> None:
        self.report.record_dealloc(AllocationType.PLAINTEXT, vid, self.ct_size, loc)
