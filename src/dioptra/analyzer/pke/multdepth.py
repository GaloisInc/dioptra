import dis

from dioptra.analyzer.pke.analysisbase import (
    AnalysisBase,
    Ciphertext,
    Plaintext,
    PublicKey,
)
from dioptra.analyzer.utils.code_loc import Frame


class MultDepth(AnalysisBase):
    depth: dict[Ciphertext, int]
    max_depth: int
    where: dict[int, tuple[int, str, dis.Positions]]
    instruction_num: int

    def __init__(self) -> None:
        self.depth = {}
        self.max_depth = 0
        self.where = {}

    def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame) -> None:
        new_depth = level
        self.set_depth(dest, new_depth, call_loc)

    def trace_encode_ckks(
        self, dest: Plaintext, value: list[float], call_loc: Frame, level: int = 0
    ) -> None:
        new_depth = level
        self.set_depth(dest, new_depth, call_loc)

    def trace_encrypt(
        self,
        dest: Ciphertext,
        publicKey: PublicKey,
        plaintext: Plaintext,
        call_loc: Frame,
    ) -> None:
        new_depth = plaintext.level
        self.set_depth(dest, new_depth, call_loc)

    def trace_decrypt(
        self,
        dest: Plaintext,
        publicKey: PublicKey,
        ciphertext: Ciphertext,
        call_loc: Frame,
    ) -> None:
        new_depth = self.depth[ciphertext]
        self.set_depth(dest, new_depth, call_loc)

    def trace_mul_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame
    ) -> None:
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth, call_loc)

    def trace_add_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame
    ) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_sub_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame
    ) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_mul_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        new_depth = max(self.depth_of(ct), self.depth_of(pt)) + 1
        self.set_depth(dest, new_depth, call_loc)

    def trace_add_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_sub_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_bootstrap(
        self, dest: Ciphertext, ct1: Ciphertext, call_loc: Frame | None
    ) -> None:
        new_depth = 0
        self.set_depth(dest, new_depth, call_loc)

    def depth_of(self, ct: Ciphertext) -> int:
        if ct in self.depth:
            return self.depth[ct]
        return 0

    def set_depth(
        self, msg: Ciphertext | Plaintext, depth: int, call_loc: Frame
    ) -> None:
        self.depth[msg] = depth
        while call_loc is not None:
            (file_name, positions) = call_loc.location()
            self.where[positions] = (depth, depth, file_name, positions)  # type: ignore
            self.max_depth = max(depth, self.max_depth)
            call_loc = call_loc.caller()
