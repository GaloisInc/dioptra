import openfhe
import time
from typing import Any, Callable, Iterable, TextIO
import enum
import json
import dioptra_native
import psutil

from dioptra.analyzer.scheme import (
    LevelInfo,
    SchemeModelBFV,
    SchemeModelBGV,
    SchemeModelCKKS,
    SchemeModelPke,
)
from dioptra.analyzer.utils.util import format_ns


class EventKind(enum.Enum):
    ENCODE = 1
    DECODE = 2
    ENCRYPT = 3
    DECRYPT = 4
    EVAL_MULT_CTCT = 5
    EVAL_ADD_CTCT = 6
    EVAL_SUB_CTCT = 7
    EVAL_BOOTSTRAP = 8
    EVAL_MULT_CTPT = 9
    EVAL_ADD_CTPT = 10
    EVAL_SUB_CTPT = 11


class Event:
    commutative_event_kinds = set(
        [
            EventKind.EVAL_ADD_CTCT,
            EventKind.EVAL_MULT_CTCT,
            EventKind.EVAL_SUB_CTCT,
            EventKind.EVAL_MULT_CTPT,
            EventKind.EVAL_ADD_CTPT,
            EventKind.EVAL_SUB_CTPT,
        ]
    )

    def __init__(
        self,
        kind: EventKind,
        arg_level1: LevelInfo | None = None,
        arg_level2: LevelInfo | None = None,
    ):
        self.kind = kind

        # if arg_depth2 is specified, arg_depth1 must be specified as well
        assert arg_level2 is None or arg_level1 is not None
        self.arg_level1 = arg_level1
        self.arg_level2 = arg_level2

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Event)
            and self.kind == value.kind
            and self.arg_level1 == value.arg_level1
            and self.arg_level2 == value.arg_level2
        )

    def __hash__(self) -> int:
        return hash((self.kind, self.arg_level1, self.arg_level2))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "arg_level1": (
                self.arg_level1.to_dict() if self.arg_level1 is not None else None
            ),
            "arg_level2": (
                self.arg_level2.to_dict() if self.arg_level2 is not None else None
            ),
        }

    def __str__(self) -> str:
        if self.arg_level2 is not None:
            return f"Event(f{self.kind.name}, f{self.arg_level1}, f{self.arg_level2})"
        elif self.arg_level1 is not None:
            return f"Event(f{self.kind.name}, f{self.arg_level1})"
        else:
            return f"Event(f{self.kind.name})"

    def is_commutative(self) -> bool:
        return self.kind in Event.commutative_event_kinds

    @staticmethod
    def from_dict(d) -> "Event":
        def read_level(s: str) -> LevelInfo | None:
            if s not in d:
                return None

            if d[s] is None:
                return None

            return LevelInfo.from_dict(d[s])

        e = Event(EventKind.ENCODE)
        e.kind = EventKind(d["kind"])
        e.arg_level1 = read_level("arg_level1")
        e.arg_level2 = read_level("arg_level2")
        return e


class RuntimeTable:
    def __init__(self, runtimes: dict[Event, int], is_bfv: bool = False):
        self.runtimes = runtimes
        self.is_bfv = is_bfv

    def reset_noise_scale_deg(self, level: LevelInfo | None) -> LevelInfo | None:
        if level is None:
            return None

        else:
            return LevelInfo(level.level, 1)

    def get_runtime_ns(self, e: Event) -> int:
        if self.is_bfv:
            e = Event(
                e.kind,
                self.reset_noise_scale_deg(e.arg_level1),
                self.reset_noise_scale_deg(e.arg_level2),
            )

        if e in self.runtimes:
            return self.runtimes[e]
        elif e.arg_level2 is not None and e.is_commutative():
            e_swaped = Event(e.kind, e.arg_level2, e.arg_level1)
            if e_swaped in self.runtimes:
                return self.runtimes[e_swaped]

        raise NotImplementedError(f"No runtime found for event: {e}")


class PKECalibrationData:
    def __init__(self, scheme: SchemeModelPke):
        self.runtime_samples: dict[Event, list[int]] = {}
        self.scheme: SchemeModelPke = scheme
        self.ct_mem: dict[LevelInfo, int] = {}
        self.pt_mem: dict[LevelInfo, int] = {}
        self.setup_memory_size = 0

    def set_memory_tables(
        self, pt_data: dict[LevelInfo, int] = {}, ct_data: dict[LevelInfo, int] = {}
    ) -> None:
        self.ct_mem = ct_data
        self.pt_mem = pt_data

    def set_plaintext_memory_dict(self, data: dict[LevelInfo, int] = {}) -> None:
        self.pt_mem = data

    def set_setup_memory_estimate(self, size: int) -> None:
        self.setup_memory_size = size

    def add_runtime_sample(self, e: Event, ns: int) -> None:
        if e not in self.runtime_samples:
            self.runtime_samples[e] = []

        self.runtime_samples[e].append(ns)

    def set_scheme(self, scheme: SchemeModelPke) -> None:
        self.scheme = scheme

    def get_scheme(self) -> SchemeModelPke:
        return self.scheme

    def to_dict(self) -> dict[str, Any]:
        assert self.scheme is not None
        evts = [(evt.to_dict(), ts) for (evt, ts) in self.runtime_samples.items()]
        ct_mems = [(lvl.to_dict(), m) for (lvl, m) in self.ct_mem.items()]
        pt_mems = [(lvl.to_dict(), m) for (lvl, m) in self.pt_mem.items()]
        return {
            "scheme": self.scheme.to_dict(),
            "runtime": evts,
            "memory": {
                "ciphertext": ct_mems,
                "plaintext": pt_mems,
                "setup": self.setup_memory_size,
            },
        }

    @staticmethod
    def from_dict(obj: dict[str, Any]) -> "PKECalibrationData":
        scheme = SchemeModelPke.from_dict(obj["scheme"])
        evts = [(Event.from_dict(evt), ts) for (evt, ts) in obj["runtime"]]
        ct_mems = [
            (LevelInfo.from_dict(lvl), m) for (lvl, m) in obj["memory"]["ciphertext"]
        ]
        pt_mems = [
            (LevelInfo.from_dict(lvl), m) for (lvl, m) in obj["memory"]["plaintext"]
        ]
        cal = PKECalibrationData(scheme)
        cal.runtime_samples = dict(evts)
        cal.pt_mem = dict(pt_mems)
        cal.ct_mem = dict(ct_mems)
        cal.setup_memory_size = obj["memory"]["setup"]
        cal.scheme = scheme
        return cal

    def write_json(self, f: str):
        with open(f, "w") as fh:
            json.dump(self.to_dict(), fh)

    @staticmethod
    def read_json(f: str) -> "PKECalibrationData":
        with open(f, "r") as fh:
            obj = json.load(fh)
            return PKECalibrationData.from_dict(obj)

    def avg_runtime_table(self) -> RuntimeTable:
        table = {}
        for event, runtimes in self.runtime_samples.items():
            table[event] = sum(runtimes) // len(runtimes)

        return RuntimeTable(table, self.scheme.name == "BFV")

    def __eq__(self, value: object) -> bool:
        def sorted(l: list) -> list:
            s = list(l)
            s.sort()
            return s

        def key_eq(k: Event) -> bool:
            return (
                isinstance(value, PKECalibrationData)
                and k in self.runtime_samples
                and k in value.runtime_samples
                and sorted(self.runtime_samples[k]) == value.runtime_samples[k]
            )

        return (
            isinstance(value, PKECalibrationData)
            and all(key_eq(k) for k in self.runtime_samples.keys())
            and all(key_eq(k) for k in value.runtime_samples.keys())
        )


class RuntimeSample:
    def __init__(
        self,
        label: Event,
        samples: PKECalibrationData,
        on_exit: Callable[[int], None] | None = None,
    ) -> None:
        self.label = label
        self.samples = samples
        self.on_exit = on_exit

    def __enter__(self):
        self.begin = time.perf_counter_ns()

    def __exit__(self, exc_type, exc_value, traceback):
        end = time.perf_counter_ns()
        t = end - self.begin
        self.samples.add_runtime_sample(self.label, t)
        if self.on_exit is not None:
            self.on_exit(t)


class PKECalibration:
    def __init__(
        self,
        cc: openfhe.CryptoContext,
        params: (
            openfhe.CCParamsBFVRNS | openfhe.CCParamsBGVRNS | openfhe.CCParamsCKKSRNS
        ),
        keypair: openfhe.KeyPair,
        features: Iterable[openfhe.PKESchemeFeature],
        out: TextIO | None = None,
        sample_count: int = 5,
    ) -> None:
        self.params = params
        self.out = out
        self.sample_count = sample_count
        self.key_pair = keypair
        self.cc = cc
        self.features = set(features)

        if self.is_ckks():
            # NOTE: the bootstrapping level is a placeholder, we will determine it experimentally
            self.scheme = SchemeModelCKKS(LevelInfo())
        elif self.is_bgv():
            self.scheme = SchemeModelBGV()
        elif self.is_bfv():
            self.scheme = SchemeModelBFV()

    def is_ckks(self) -> bool:
        return isinstance(self.params, openfhe.CCParamsCKKSRNS)

    def is_bgv(self) -> bool:
        return isinstance(self.params, openfhe.CCParamsBGVRNS)

    def is_bfv(self) -> bool:
        return isinstance(self.params, openfhe.CCParamsBFVRNS)

    def log(self, msg: str) -> None:
        if self.out is not None:
            print(msg, file=self.out)

    def num_slots(self) -> int:
        if isinstance(self.params, openfhe.CCParamsCKKSRNS):
            assert (
                self.params.GetRingDim().bit_count() == 1
            ), "CKKS ring dimension should be a power of 2"
            return self.params.GetRingDim() >> 1
        else:
            return self.cc.GetRingDimension()  ## XXX: ask hilder about this

    def encode(self, level: LevelInfo) -> openfhe.Plaintext:
        pt_val = [0] * self.num_slots()
        if isinstance(self.params, openfhe.CCParamsCKKSRNS):
            return self.cc.MakeCKKSPackedPlaintext(
                pt_val,
                slots=self.num_slots(),
                level=level.level,
                scaleDeg=level.noise_scale_deg,
            )
        else:
            return self.cc.MakePackedPlaintext(
                pt_val, level=level.level, noiseScaleDeg=level.noise_scale_deg
            )

    def decode(self, pt: openfhe.Plaintext) -> None:
        if isinstance(self.params, openfhe.CCParamsCKKSRNS):
            pt.GetRealPackedValue()
        else:
            pt.GetPackedValue()

    def all_levels(self) -> Iterable[LevelInfo]:
        if self.is_ckks():
            for deg in [1, 2]:
                for level in range(0, self.params.GetMultiplicativeDepth() - (deg - 1)):
                    yield LevelInfo(level, deg)

        if self.is_bgv():
            yield LevelInfo(0, 2)
            for deg in [1, 2]:
                for level in range(1, self.params.GetMultiplicativeDepth()):
                    yield LevelInfo(level, deg)

        # dunno how to think about noise scale deg in this case
        if self.is_bfv():
            for level in range(0, 2):  # TODO: ask hilder what the proper level is here
                yield LevelInfo(level, 1)

    def level_pairs(self) -> Iterable[tuple[LevelInfo, LevelInfo]]:
        if self.is_bfv():
            for l in self.all_levels():
                yield (l, l)

        else:
            for l1 in self.all_levels():
                for l2 in self.all_levels():
                    yield (l1, l2)

    def level_pairs_comm(self) -> Iterable[tuple[LevelInfo, LevelInfo]]:
        if self.is_bfv():
            for i in self.level_pairs():
                yield i

        else:
            all = list(self.all_levels())
            for i in range(0, len(all)):
                for j in range(i, len(all)):
                    yield (all[i], all[j])

    def calibrate_base(self) -> PKECalibrationData:
        setup_size = psutil.Process().memory_info().rss
        samples = PKECalibrationData(self.scheme)
        samples.set_setup_memory_estimate(setup_size)
        ct_mem: dict[LevelInfo, int] = {}
        pt_mem: dict[LevelInfo, int] = {}

        def measure(
            label: EventKind, a1: LevelInfo | None = None, a2: LevelInfo | None = None
        ):
            if a1 is None and a2 is None:
                self.log(f"Measuring {label}")

            elif a2 is None:
                self.log(f"Measuring {label} depth={a1}")

            else:
                self.log(f"Measuring {label} level1={a1} level2={a2}")

            def on_exit(ns: int):
                self.log(f"   [{format_ns(ns)}]")

            return RuntimeSample(Event(label, a1, a2), samples, on_exit=on_exit)

        cc = self.cc
        key_pair = self.key_pair

        max_mult_depth = self.params.GetMultiplicativeDepth()
        self.log(f"Max multiplicative depth: {max_mult_depth}")
        self.log(f"Slots: {self.num_slots()}")
        bootstrap_lev = None

        for iteration in range(0, self.sample_count):
            self.log(f"Iteration {iteration}")

            # XXX: is this its own function?
            if openfhe.PKESchemeFeature.FHE in self.features and self.is_ckks():
                pt = self.encode(LevelInfo(max_mult_depth - 1, 1))
                ct = cc.Encrypt(key_pair.publicKey, pt)
                bsres = None
                with measure(EventKind.EVAL_BOOTSTRAP):
                    bsres = cc.EvalBootstrap(ct)

                if bootstrap_lev is None:
                    bootstrap_lev = LevelInfo(level=bsres.GetLevel(), noise_scale_deg=2)
                    # update scheme with bootstrapping data
                    samples.set_scheme(SchemeModelCKKS(bootstrap_lev))
                    self.log(f"Bootstrap level: {bootstrap_lev}")

            for level in self.all_levels():
                with measure(EventKind.ENCODE, level):
                    pt = self.encode(level)

                with measure(EventKind.ENCRYPT, level):
                    ct = cc.Encrypt(key_pair.publicKey, pt)

                with measure(EventKind.DECRYPT, level):
                    cc.Decrypt(key_pair.secretKey, ct)

                with measure(EventKind.DECODE, level):
                    self.decode(pt)

                if level not in ct_mem:
                    ct_size = dioptra_native.ciphertext_size(ct)
                    self.log(f"Ciphertext {level}: {ct_size}")
                    ct_mem[level] = ct_size

                if level not in pt_mem:
                    pt_size = dioptra_native.plaintext_size(pt)
                    self.log(f"Plaintext {level}: {pt_size}")
                    pt_mem[level] = pt_size

            for level1, level2 in self.level_pairs_comm():
                pt = self.scheme.arbitrary_pt(self.cc, level2)
                ct1 = self.scheme.arbitrary_ct(self.cc, self.key_pair.publicKey, level1)
                ct2 = self.scheme.arbitrary_ct(self.cc, self.key_pair.publicKey, level2)

                with measure(EventKind.EVAL_ADD_CTCT, level1, level2):
                    cc.EvalAdd(ct1, ct2)

                with measure(EventKind.EVAL_MULT_CTCT, level1, level2):
                    cc.EvalMult(ct1, ct2)

                with measure(EventKind.EVAL_SUB_CTCT, level1, level2):
                    cc.EvalSub(ct1, ct2)

                with measure(EventKind.EVAL_MULT_CTPT, level1, level2):
                    cc.EvalMult(ct1, pt)

                with measure(EventKind.EVAL_ADD_CTPT, level1, level2):
                    cc.EvalMult(ct1, pt)

                with measure(EventKind.EVAL_ADD_CTPT, level1, level2):
                    cc.EvalSub(ct1, pt)

        samples.set_memory_tables(pt_mem, ct_mem)
        return samples

    def calibrate(self) -> PKECalibrationData:
        self.log("Beginning calibration...")
        return self.calibrate_base()
