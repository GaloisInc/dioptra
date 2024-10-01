from enum import Enum
from dioptra.analyzer.pke.analysisbase import AnalysisBase, Ciphertext, Plaintext
from dioptra.analyzer.report.memory import AllocationType, MemoryReport
from dioptra.analyzer.scheme import LevelInfo
from dioptra.analyzer.utils.code_loc import Frame


class PKEMemoryEstimate(AnalysisBase):
    def __init__(
        self,
        setup_size: int,
        ct_size: dict[LevelInfo, int],
        pt_size: dict[LevelInfo, int],
        report: MemoryReport,
    ):
        self.ct_size = ct_size
        self.pt_size = pt_size
        self.report = report
        report.record_setup_size(setup_size)

    def trace_alloc_ct(self, ct: Ciphertext, call_loc: Frame | None) -> None:
        self.report.record_alloc(
            AllocationType.CIPHERTEXT, ct.id, self.ct_size[ct.level], call_loc
        )

    def trace_dealloc_ct(
        self, vid: int, level: LevelInfo, call_loc: Frame | None
    ) -> None:
        self.report.record_dealloc(
            AllocationType.CIPHERTEXT, vid, self.ct_size[level], call_loc
        )

    def trace_alloc_pt(self, pt: Plaintext, call_loc: Frame | None) -> None:
        self.report.record_alloc(
            AllocationType.PLAINTEXT, pt.id, self.pt_size[pt.level], call_loc
        )

    def trace_dealloc_pt(
        self, vid: int, level: LevelInfo, call_loc: Frame | None
    ) -> None:
        self.report.record_dealloc(
            AllocationType.PLAINTEXT, vid, self.pt_size[level], call_loc
        )
