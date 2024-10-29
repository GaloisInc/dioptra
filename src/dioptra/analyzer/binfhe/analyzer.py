from typing import Callable
import weakref
from dioptra.analyzer.binfhe.params import BinFHEParams
from dioptra.analyzer.binfhe.value import LWECiphertext, LWEPrivateKey
import openfhe

from dioptra.analyzer.utils import code_loc
from dioptra.analyzer.utils.code_loc import Frame, TraceLoc, calling_frame
from dioptra.analyzer.utils.error import NotSupportedException


class BinFHEAnalysisBase:
    def trace_keygen(self, key: LWEPrivateKey, loc: Frame | None) -> None:
        pass

    def trace_encrypt(
        self, dest: LWECiphertext, sk: LWEPrivateKey, loc: Frame | None
    ) -> None:
        pass

    def trace_decrypt(
        self, sk: LWEPrivateKey, ct: LWECiphertext, loc: Frame | None
    ) -> None:
        pass

    def trace_eval_gate(
        self,
        gate: openfhe.BINGATE,
        dest: LWECiphertext,
        c1: LWECiphertext,
        c2: LWECiphertext,
        loc: Frame | None,
    ) -> None:
        pass

    def trace_eval_not(
        self, dest: LWECiphertext, c: LWECiphertext, loc: Frame | None
    ) -> None:
        pass

    def trace_alloc_ct(self, dest: LWECiphertext, loc: Frame | None) -> None:
        pass

    def trace_dealloc_ct(self, vid: int, loc: Frame | None) -> None:
        pass

    def trace_send_ct(self, ct: LWECiphertext, nm: NetworkModel, loc: Frame | None) -> None:
        pass

    def trace_recv_ct(self, ct: LWECiphertext, nm: NetworkModel, loc: Frame | None) -> None:
        pass

class BinFHEAnalysisGroup(BinFHEAnalysisBase):
    def __init__(self, grp: list[BinFHEAnalysisBase]) -> None:
        self.analyses = grp

    def trace_keygen(self, key: LWEPrivateKey, loc: Frame | None) -> None:
        for a in self.analyses:
            a.trace_keygen(key, loc)

    def trace_encrypt(
        self, dest: LWECiphertext, sk: LWEPrivateKey, loc: Frame | None
    ) -> None:
        for a in self.analyses:
            a.trace_encrypt(dest, sk, loc)

    def trace_decrypt(
        self, sk: LWEPrivateKey, ct: LWECiphertext, loc: Frame | None
    ) -> None:
        for a in self.analyses:
            a.trace_decrypt(sk, ct, loc)

    def trace_eval_gate(
        self,
        gate: openfhe.BINGATE,
        dest: LWECiphertext,
        c1: LWECiphertext,
        c2: LWECiphertext,
        loc: Frame | None,
    ) -> None:
        for a in self.analyses:
            a.trace_eval_gate(gate, dest, c1, c2, loc)

    def trace_eval_not(
        self, dest: LWECiphertext, c: LWECiphertext, loc: Frame | None
    ) -> None:
        for a in self.analyses:
            a.trace_eval_not(dest, c, loc)

    def trace_alloc_ct(self, dest: LWECiphertext, loc: Frame | None) -> None:
        for a in self.analyses:
            a.trace_alloc_ct(dest, loc)

    def trace_dealloc_ct(self, vid: int, loc: Frame | None) -> None:
        for a in self.analyses:
            a.trace_dealloc_ct(vid, loc)


class BinFHENetwork:
    """This class represents a simulated nework and should only ever be
    constructed by calling `MakeNetwork` on an analyzer class.
    """
    
    def __init__(self, analyzer: 'BinFHEAnalyzer', model: NetworkModel) -> None:
        self.net_model = model
        self.analyzer = analyzer

    def SendCiphertext(self, ct: LWECiphertext) -> None:
        """Simulate sending a ciphertext over the this network."""
        self.analyzer._send_ciphertext(ct, self.net_model, code_loc.calling_frame())

    def RecvCiphertext(self, ct: LWECiphertext) -> None:
        """Simulate receiving a ciphertext over this network."""
        self.analyzer._recv_ciphertext(ct, self.net_model, code_loc.calling_frame())

# TODO: figure out plaintext modulus for p != 4
class BinFHEAnalyzer:
    def __init__(
        self,
        params: BinFHEParams,
        analysis: BinFHEAnalysisBase,
        trace: TraceLoc | None = None,
    ) -> None:
        self.params = params
        self.analysis = analysis
        self.trace = trace

    def _unsupported_feature_msg(self, feature: str) -> str:
        return f"{feature} is not supported for estimation in the current version of dioptra"

    def _check_plaintext_modulus(self, n: int, frame: Frame|None) -> None:
        if n != 4:
            raise NotSupportedException(
                f"Non-default plaintext modulus ({n}) is not supported on this operation in the current version of dioptra",
                frame
            )

    def BTKeyGen(
        self,
        sk: LWEPrivateKey,
        keygenMode: openfhe.KEYGEN_MODE = openfhe.KEYGEN_MODE.SYM_ENCRYPT,
    ) -> None:
        pass

    def Decrypt(self, sk: LWEPrivateKey, ct: LWECiphertext, p: int = 4) -> int:
        loc = code_loc.calling_frame()
        self._check_plaintext_modulus(p, loc)
        self.analysis.trace_decrypt(sk, ct, loc)
        return ct.value  # TODO: value is not correct

    def Encrypt(
        self,
        sk: LWEPrivateKey,
        m: int,
        output: openfhe.BINFHE_OUTPUT = openfhe.BINFHE_OUTPUT.BOOTSTRAPPED,  # XXX: TODO
        p: int = 4,
        mod: int = 0,
    ) -> LWECiphertext:
        loc = code_loc.calling_frame()
        self._check_plaintext_modulus(p, loc)
        if m != 0 and m != 1:
            raise NotSupportedException(
                "Plaintext must be binary (0 or 1) in the current version of dioptra", loc
            )

        ct = LWECiphertext(
            length=self.params.n, modulus=self.params.q, value=m, pt_mod=p
        )
        self.analysis.trace_encrypt(ct, sk, loc)
        return ct

    def _eval_gate_plain(self, gate: openfhe.BINGATE, i1: int, i2: int) -> int:
        if gate == openfhe.BINGATE.OR:
            return i1 | i2

        elif gate == openfhe.BINGATE.AND:
            return i1 & i2

        elif gate == openfhe.BINGATE.NOR:
            return (~(i1 | i2)) & 1

        elif gate == openfhe.BINGATE.NAND:
            return (~(i1 & i2)) & 1

        elif gate == openfhe.BINGATE.XOR_FAST or gate == openfhe.BINGATE.XOR:
            return i1 ^ i2

        elif gate == openfhe.BINGATE.XNOR_FAST or gate == openfhe.BINGATE.XNOR:
            return (~(i1 ^ i2)) & 1

        raise NotImplementedError(f"gate type not implemented: {gate.name}")

    def EvalBinGate(
        self, gate: openfhe.BINGATE, ct1: LWECiphertext, ct2: LWECiphertext
    ) -> LWECiphertext:
        loc = code_loc.calling_frame()
        dest = self._mk_ct(self._eval_gate_plain(gate, ct1.value, ct2.value), loc)
        self.analysis.trace_eval_gate(gate, dest, ct1, ct2, loc)
        return dest

    # TODO: need to figure out how long the resulting list is - ask Hilder
    def EvalDecomp(self, ct: LWECiphertext) -> list[LWECiphertext]:
        raise NotSupportedException.fn_not_impl("EvalDecomp")

    def EvalFloor(self, ct: LWECiphertext, roundbits: int = 0) -> LWECiphertext:
        raise NotSupportedException.fn_not_impl("EvalFloor")

    def EvalFunc(self, ct: LWECiphertext, LUT: list[int]) -> LWECiphertext:
        raise NotSupportedException.fn_not_impl("EvalFunc")

    def EvalNOT(self, ct: LWECiphertext) -> LWECiphertext:
        loc = code_loc.calling_frame()
        dest = self._mk_ct(~ct.value & 1, loc)
        self.analysis.trace_eval_not(dest, ct, loc)
        return dest

    def EvalSign(self, ct: LWECiphertext) -> LWECiphertext:
        raise NotSupportedException.fn_not_impl("EvalSign")

    def GenerateBinFHEContext(self, *args, **kwargs):
        pass  # TODO: we can probably ingore this for now

    def GenerateLUTviaFunction(self, f: Callable[[int, int], int], p: int) -> list[int]:
        raise NotSupportedException.fn_not_impl("GenerateLUTviaFunction")

    def GetBeta(self) -> int:
        return self.params.beta

    def Getn(self) -> int:
        return self.params.n

    def Getq(self) -> int:
        return self.params.q

    def KeyGen(self) -> LWEPrivateKey:
        return LWEPrivateKey(self.params.n)
    
    def MakeNetwork(self, send_bps: BPS, recv_bps: BPS, latency_ms: int) -> BinFHENetwork:
        """Create a simulated network with the given parameters."""
        nm = NetworkModel(send_bps.bps, recv_bps.bps, latency=latency_ms * 10**6)
        return BinFHENetwork(self, nm)
    
    def ArbitraryCT(self) -> LWECiphertext:
        return LWECiphertext(
            length=self.params.n, modulus=self.params.q, value=0, pt_mod=4
        )

    def _dealloc_ct(self, vid: int):
        loc = None
        if self.trace is not None:
            loc = self.trace.get_current_frame()
        self.analysis.trace_dealloc_ct(vid, loc)

    def _mk_ct(self, value: int, loc: Frame | None) -> LWECiphertext:
        new = LWECiphertext(self.params.n, self.params.q, value, 4)
        self.analysis.trace_alloc_ct(new, loc)
        new._set_finalizer(weakref.finalize(new, self._dealloc_ct, new.id))
        return new
    
    def _send_ciphertext(self, ct: LWECiphertext, nm: NetworkModel, loc: Frame|None):
        self.analysis.trace_send_ct(ct, nm, loc)

    def _recv_ciphertext(self, ct: LWECiphertext, nm: NetworkModel, loc: Frame|None):
        self.analysis.trace_recv_ct(ct, nm, loc)
