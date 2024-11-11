import json
import time
from typing import IO, Any, Callable

import openfhe
import psutil

import dioptra_native
from dioptra.binfhe.event import BinFHEEvent, BinFHEEventKind
from dioptra.binfhe.params import BinFHEParams
from dioptra.utils.util import format_ns


class BinFHECalibrationData:
    def __init__(self, params: BinFHEParams):
        self.runtime_samples: dict[BinFHEEvent, list[int]] = {}
        self.params = params
        self.ciphertext_size: int = 0
        self.setup_memory_size: int = 0

    def set_ciphertext_size(self, ctsize: int):
        self.ciphertext_size = ctsize

    def add_runtime_sample(self, event: BinFHEEvent, runtime: int) -> None:
        if event not in self.runtime_samples:
            self.runtime_samples[event] = []

        self.runtime_samples[event].append(runtime)

    def set_setup_memory_estimate(self, size: int) -> None:
        self.setup_memory_size = size

    def avg_case(self) -> dict[BinFHEEvent, int]:
        return dict([(e, sum(s) // len(s)) for (e, s) in self.runtime_samples.items()])

    def to_dict(self) -> dict[str, Any]:
        scheme = {"name": "BINFHE", "params": self.params.to_dict()}
        runtime_samples = [(e.to_dict(), s) for (e, s) in self.runtime_samples.items()]

        return {
            "scheme": scheme,
            "runtime_samples": runtime_samples,
            "memory": {
                "ciphertext": self.ciphertext_size,
                "setup": self.setup_memory_size,
            },
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "BinFHECalibrationData":
        assert d["scheme"]["name"] == "BINFHE"
        params = BinFHEParams.from_dict(d["scheme"]["params"])
        cd = BinFHECalibrationData(params)
        cd.runtime_samples = dict(
            [(BinFHEEvent.from_dict(e), s) for (e, s) in d["runtime_samples"]]
        )
        cd.ciphertext_size = d["memory"]["ciphertext"]
        cd.setup_memory_size = d["memory"]["setup"]
        return cd

    def write_json(self, file: str) -> None:
        with open(file, "w") as f:
            json.dump(self.to_dict(), f)

    @staticmethod
    def read_json(file: str) -> "BinFHECalibrationData":
        with open(file) as f:
            return BinFHECalibrationData.from_dict(json.load(f))


# TODO: factor this so it is usable more places
class RuntimeSample:
    def __init__(
        self,
        label: BinFHEEvent,
        samples: BinFHECalibrationData,
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


class BinFHECalibration:
    def __init__(
        self,
        cc: openfhe.BinFHEContext,
        sk: openfhe.LWEPrivateKey,
        log: IO | None = None,
        sample_count: int = 5,
    ):
        self.cc = cc
        self.sk = sk
        self.iter = sample_count
        self.log_out = log

    def log(self, s: str):
        if self.log_out is not None:
            print(s, file=self.log_out)

    def run(self) -> BinFHECalibrationData:
        params = BinFHEParams(self.cc.Getn(), self.cc.Getq(), self.cc.GetBeta())
        data = BinFHECalibrationData(params)
        setup_size = psutil.Process().memory_info().rss
        data.set_setup_memory_estimate(setup_size)

        def measure(e: BinFHEEvent):
            self.log(f"Measuring {e}")

            def logtime(t):
                self.log(f" [{format_ns(t)}]")

            return RuntimeSample(e, data, on_exit=logtime)

        # measure ciphertext size
        ct = self.cc.Encrypt(self.sk, 0)
        ct_size = dioptra_native.lwe_ciphertext_size(ct)
        data.set_ciphertext_size(ct_size)
        self.log(f"Ciphertext size: {ct_size}")
        ct = None

        for i in range(0, self.iter):
            ct1 = None

            with measure(BinFHEEvent(BinFHEEventKind.KEYGEN)):
                self.cc.KeyGen()

            with measure(BinFHEEvent(BinFHEEventKind.ENCRYPT)):
                ct1 = self.cc.Encrypt(self.sk, 1)

            with measure(BinFHEEvent(BinFHEEventKind.DECRYPT)):
                self.cc.Decrypt(self.sk, ct1)

            ct2 = self.cc.Encrypt(self.sk, 0)

            for gate, event in BinFHEEvent.bingate_to_event().items():
                with measure(event):
                    self.cc.EvalBinGate(gate, ct1, ct2)

            with measure(BinFHEEvent(BinFHEEventKind.EVAL_NOT)):
                self.cc.EvalNOT(ct1)

            # TODO: these only seem to work with high precision (what's that?)

            # decomp_result = None
            # with measure(Event(EventKind.EVAL_DECOMP)):
            #   decomp_result = self.cc.EvalDecomp(ct1)

            # self.log(f"Decomp size: {len(decomp_result)}")
            # decomp_result = None

            # with measure(Event(EventKind.EVAL_SIGN)):
            #   self.cc.EvalSign(ct1)

            # with measure(Event(EventKind.EVAL_FLOOR)):
            #   self.cc.EvalFloor(ct1)

            # TODO: LUTS cause a segmentation fault on exit

            # lut = None
            # def id_fn(x, y):
            #   return x

            # lut = None
            # with measure(Event(EventKind.GENERATE_LUT_VIA_FUNCTION)):
            #   lut = self.cc.GenerateLUTviaFunction(id_fn, 4) # XXX: does this need to be calibrated based on pt size?

            # self.log(f"LUT size: {len(lut)}")
            # with measure(Event(EventKind.EVAL_FUNC)):
            #   self.cc.EvalFunc(ct1, lut)

            # lut = None

        return data
