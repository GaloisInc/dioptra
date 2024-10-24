
import math
from typing import Any, Callable, Iterable, Self, Sequence, TypeVar
import weakref
from dioptra.analyzer.scheme import LevelInfo, SchemeModelPke
from dioptra.analyzer.utils import code_loc
from dioptra.analyzer.utils.code_loc import Frame, TraceLoc
import dis
import os.path

from dioptra.analyzer.utils.network import NetworkModel
from dioptra.analyzer.utils.util import BPS

class VectorMath:
    @staticmethod
    def pw_mul(i1: Iterable | None, i2: Iterable | None) -> Iterable | None:
        """Pointwise multiplication."""
        if i1 is None or i2 is None:
            return None

        return [v1 * v2 for (v1, v2) in zip(i1, i2)]

    @staticmethod
    def pw_add(i1: Iterable | None, i2: Iterable | None) -> Iterable | None:
        """Pointwise multiplication."""
        if i1 is None or i2 is None:
            return None
        return [v1 + v2 for (v1, v2) in zip(i1, i2)]

    @staticmethod
    def pw_sub(i1: Iterable | None, i2: Iterable | None) -> Iterable | None:
        """Pointwise multiplication."""
        if i1 is None or i2 is None:
            return None
        return [v1 - v2 for (v1, v2) in zip(i1, i2)]


class Value:
    value_id = 0

    @staticmethod
    def fresh_id() -> int:
        id = Value.value_id
        Value.value_id += 1
        return id

    def __init__(self) -> None:
        self.id = Value.fresh_id()

    def __hash__(self) -> int:
        return self.id.__hash__()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Value):
            return self.id == value.id
        return False


class PrivateKey(Value):
    pass


class Ciphertext(Value):
    def __init__(self, level: LevelInfo = LevelInfo(), value: Any = None):
        super().__init__()
        self.value = value
        self.level = level

    def set_finalizer(self, finalizer: weakref.finalize) -> Self:
        self._finalizer = finalizer
        return self


class Plaintext(Value):
    def __init__(self, level: LevelInfo = LevelInfo(), value: Any = None):
        super().__init__()
        self.value = value
        self.level = level

    def GetPackedValue(self):
        if self.value is None:
            raise ValueError("GetPackedValue(): Does not work for arbitrary values")

        return list(self.value)

    def GetRealPackedValue(self):
        if self.value is None:
            raise ValueError("GetRealPackedValue(): Does not work for arbitrary values")

        return list(self.value)

    def set_finalizer(self, finalizer: weakref.finalize) -> Self:
        self._finalizer = finalizer
        return self


class PublicKey(Value):
    pass


class KeyPair:
    publicKey: PublicKey
    secretKey: PrivateKey

    def __init__(self, sk: PrivateKey, pk: PublicKey):
        self.publicKey = pk
        self.secretKey = sk


class AnalysisBase:
    where: dict[int | dis.Positions, tuple[int, str, str, dis.Positions]]

    def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame | None) -> None:
        pass

    def trace_encode_ckks(self, dest: Plaintext, call_loc: Frame | None) -> None:
        pass

    def trace_encrypt(
        self, dest: Ciphertext, pt: Plaintext, key: PublicKey, call_loc: Frame | None
    ) -> None:
        pass

    def trace_decrypt(
        self, dest: Plaintext, ct1: Ciphertext, key: PrivateKey, call_loc: Frame | None
    ) -> None:
        pass

    def trace_bootstrap(
        self, dest: Ciphertext, ct1: Ciphertext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_mul_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_add_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_sub_ctct(
        self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_mul_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_add_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_sub_ctpt(
        self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None
    ) -> None:
        pass

    def trace_alloc_ct(self, ct: Ciphertext, call_loc: Frame | None) -> None:
        pass

    def trace_alloc_pt(self, pt: Plaintext, call_loc: Frame | None) -> None:
        pass

    def trace_dealloc_ct(
        self, vid: int, level: LevelInfo, call_loc: Frame | None
    ) -> None:
        pass

    def trace_dealloc_pt(
        self, vid: int, level: LevelInfo, call_loc: Frame | None
    ) -> None:
        pass


class Network:
    def __init__(self, analyzer: 'Analyzer', model: NetworkModel) -> None:
        self.net_model = model
        self.analyzer = analyzer

    def SendCiphertext(self, ct: Ciphertext) -> None:
        self.analyzer._send_ciphertext(ct, self.net_model, code_loc.calling_frame())

    def RecvCiphertext(self, ct: Ciphertext) -> None:
        self.analyzer._recv_ciphertext(ct, self.net_model, code_loc.calling_frame())


class Analyzer:
    analysis_list: list[AnalysisBase]

    def __init__(
        self,
        analysis_list: list[AnalysisBase],
        scheme: SchemeModelPke,
        trace_loc: TraceLoc | None = None,
    ):
        self.analysis_list = analysis_list
        self.scheme = scheme
        self.trace_loc = trace_loc

    def KeyGen(self) -> KeyPair:
        return KeyPair(PrivateKey(), PublicKey())

    def EvalMultKeyGen(self, sk: PrivateKey) -> None:
        pass

    def EvalRotateKeyGen(self, sk: PrivateKey, index_list: list[int]) -> None:
        pass

    def MakePackedPlaintext(
        self, value: list[int], noise_scale_deg: int = 1, level: int = 0
    ) -> Plaintext:
        caller_loc = code_loc.calling_frame()
        lv = LevelInfo(level, noise_scale_deg).max(self.scheme.min_level())
        new = self._mk_pt(lv, value, caller_loc)
        for analysis in self.analysis_list:
            analysis.trace_encode(new, level, caller_loc)
        return new

    def MakeCKKSPackedPlaintext(self, *args, **kwargs) -> Plaintext:  # type: ignore
        level = kwargs.get("level", 0)
        noise_scale_deg = kwargs.get("scaleDeg", 1)

        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], list):
            new = self._mk_pt(LevelInfo(level, noise_scale_deg), args[0], caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_encode_ckks(new, caller_loc)
            return new
        raise NotImplementedError(
            "MakeCKKSPackedPlaintext: analyzer does not implement this overload"
        )

    def Encrypt(self, public_key: PublicKey, plaintext: Plaintext) -> Ciphertext:
        caller_loc = code_loc.calling_frame()
        new = self._mk_ct(level=plaintext.level, value=plaintext.value, loc=caller_loc)
        for analysis in self.analysis_list:
            analysis.trace_encrypt(new, plaintext, public_key, caller_loc)
        return new

    def Decrypt(self, *args, **kwargs):
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], PrivateKey) and isinstance(args[1], Ciphertext):
            pkey = args[0]
            ct = args[1]
            new = self._mk_pt(ct.level, ct.value, caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_decrypt(new, ct, pkey, caller_loc)
            return new

        raise NotImplementedError("Decrypt: analyzer does not implement this overload")

    def EvalMult(self, *args, **kwargs) -> Ciphertext:  # type: ignore
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            level = self.scheme.mul_level(args[0].level, args[1].level)
            new = self._mk_ct(level, VectorMath.pw_mul(args[0].value, args), caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_mul_ctct(new, args[0], args[1], caller_loc)
            return new

        elif isinstance(args[0], Ciphertext) and isinstance(args[1], Plaintext):
            level = self.scheme.mul_level(args[0].level, args[1].level)
            new = self._mk_ct(
                level, VectorMath.pw_mul(args[0].value, args[1].value), caller_loc
            )
            for analysis in self.analysis_list:
                analysis.trace_mul_ctpt(new, args[0], args[1], caller_loc)
            return new

        raise NotImplementedError("EvalMult: analyzer does not implement this overload")

    def EvalAdd(self, *args, **kwargs) -> Ciphertext:  # type: ignore
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            level = self.scheme.add_level(args[0].level, args[1].level)
            new = self._mk_ct(level, VectorMath.pw_add(args[0].value, args), caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_add_ctct(new, args[0], args[1], caller_loc)
            return new

        elif isinstance(args[0], Ciphertext) and isinstance(args[1], Plaintext):
            level = self.scheme.add_level(args[0].level, args[1].level)
            new = self._mk_ct(level, VectorMath.pw_add(args[0].value, args), caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_add_ctpt(new, args[0], args[1], caller_loc)
            return new

        raise NotImplementedError("EvalAdd: analyzer does not implement this overload")

    def EvalSub(self, *args, **kwargs) -> Ciphertext:  # type: ignore
        caller_loc = code_loc.calling_frame()

        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            level = self.scheme.add_level(args[0].level, args[1].level)
            new = self._mk_ct(level, VectorMath.pw_add(args[0].value, args), caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_sub_ctct(new, args[0], args[1], caller_loc)
            return new

        elif isinstance(args[0], Ciphertext) and isinstance(args[1], Plaintext):
            level = self.scheme.add_level(args[0].level, args[1].level)
            new = self._mk_ct(level, VectorMath.pw_sub(args[0].value, args), caller_loc)
            for analysis in self.analysis_list:
                analysis.trace_sub_ctpt(new, args[0], args[1], caller_loc)
            return new

        raise NotImplementedError("EvalAdd: analyzer does not implement this overload")

    def EvalBootstrap(
        self, ciphertext: Ciphertext, _numIterations: int = 1, _precision: int = 0
    ) -> Ciphertext:
        caller_loc = code_loc.calling_frame()
        new = self._mk_ct(
            level=self.scheme.bootstrap_level(ciphertext.level),
            value=ciphertext.value,
            loc=caller_loc,
        )
        for analysis in self.analysis_list:
            analysis.trace_bootstrap(new, ciphertext, caller_loc)
        return new

    def ArbitraryCT(self, level=0, noiseScaleDeg=1) -> Ciphertext:
        caller_loc = code_loc.calling_frame()
        lv = LevelInfo(level, noiseScaleDeg).max(self.scheme.min_level())
        return self._mk_ct(lv, None, caller_loc)
    
    def MakeNetwork(self, send_bps: BPS, recv_bps: BPS, latency_ms: int) -> Network:
        nm = NetworkModel(send_bps.bps, recv_bps.bps, latency=latency_ms * 10**6)
        return Network(self, nm)

    def _dealloc_ct(self, vid: int, level: LevelInfo) -> None:
        loc = None
        if self.trace_loc is not None:
            loc = self.trace_loc.get_current_frame()

        for analysis in self.analysis_list:
            analysis.trace_dealloc_ct(vid, level, loc)

    def _dealloc_pt(self, vid: int, level: LevelInfo) -> None:
        loc = None
        if self.trace_loc is not None:
            loc = self.trace_loc.get_current_frame()

        for analysis in self.analysis_list:
            analysis.trace_dealloc_pt(vid, level, loc)

    def _mk_ct(self, level: LevelInfo, value: Any, loc: Frame | None) -> Ciphertext:
        ct = Ciphertext(level=level, value=value)
        for analysis in self.analysis_list:
            analysis.trace_alloc_ct(ct, loc)
        ct.set_finalizer(weakref.finalize(ct, self._dealloc_ct, ct.id, level))
        return ct

    def _mk_pt(self, level: LevelInfo, value: Any, loc: Frame | None) -> Plaintext:
        pt = Plaintext(level=level, value=value)
        for analysis in self.analysis_list:
            analysis.trace_alloc_pt(pt, loc)
        pt.set_finalizer(weakref.finalize(pt, self._dealloc_ct, pt.id, level))
        return pt
    
    def _send_ciphertext(self, ct: Ciphertext, nm: NetworkModel, loc: Frame|None):
        for analysis in self.analysis_list:
            analysis.trace_send_ct(ct, nm, loc)

    def _recv_ciphertext(self, ct: Ciphertext, nm: NetworkModel, loc: Frame|None):
        for analysis in self.analysis_list:
            analysis.trace_recv_ct(ct, nm, loc)

    
    # def _enable_trace(self):
    #     sys.settrace(self._trace)

    # def _trace(self, frame: any, event: str, arg: any) -> function:
    #     if event == 'call':
    #         caller = frame.f_back
    #         print(f"calling {frame.f_code.co_qualname} at {frame_loc(caller)}")

    #     if event == 'return' and frame.f_back is not None:
    #         caller = frame.f_back
    #         print(f"return from {frame.f_code.co_qualname} to {caller.f_code.co_qualname} at {frame_loc(caller)}")
    #     return self._trace
