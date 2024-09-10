import json
from random import sample
import time
from typing import IO, Any, Callable
import openfhe

from dioptra.analyzer.binfhe.event import Event, EventKind
from dioptra.analyzer.utils.util import format_ns

class CalibrationData:
  def __init__(self):
    self.runtime_samples : dict[Event, list[int]] = {}

  def add_runtime_sample(self, event: Event, runtime: int) -> None:
    if event not in self.runtime_samples:
      self.runtime_samples[event] = []

    self.runtime_samples[event].append(runtime)

  def to_dict(self) -> dict[str, Any]:
    scheme = {"scheme": "binfhe"}
    runtime_samples = [(e.to_dict(), s) for (e, s) in self.runtime_samples.items()]

    return {
      "scheme": scheme,
      "runtime_samples": runtime_samples
    }
    
  @staticmethod
  def from_dict(d: dict[str, Any]) -> 'CalibrationData':
    cd = CalibrationData()
    cd.runtime_samples = dict([(Event.from_dict(e), s) for (e, s) in d["runtime_samples"]])
    return cd
  
  def write_json(self, file: str) -> None:
    with open(file, "w") as f:
      json.dump(self.to_dict(), f)

  @staticmethod
  def read_json(file: str) -> 'CalibrationData':
    with open(file) as f:
      return CalibrationData.from_dict(json.load(f))

# TODO: factor this so it is usable more places
class RuntimeSample:
  def __init__(self, label: Event, samples: CalibrationData, on_exit: Callable[[int], None] | None = None) -> None:
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

class Calibration:
  bingate_to_event = {
    openfhe.BINGATE.OR: Event(EventKind.EVAL_BIN_GATE_OR),
    openfhe.BINGATE.AND: Event(EventKind.EVAL_BIN_GATE_AND),
    openfhe.BINGATE.NOR: Event(EventKind.EVAL_BIN_GATE_NOR),
    openfhe.BINGATE.NAND: Event(EventKind.EVAL_BIN_GATE_NAND),
    openfhe.BINGATE.XOR_FAST: Event(EventKind.EVAL_BIN_GATE_XORFAST),
    openfhe.BINGATE.XNOR_FAST: Event(EventKind.EVAL_BIN_GATE_XNORFAST),
    openfhe.BINGATE.XOR: Event(EventKind.EVAL_BIN_GATE_XOR),
    openfhe.BINGATE.XNOR: Event(EventKind.EVAL_BIN_GATE_XNOR),
  }

  def __init__(self, 
               cc: openfhe.BinFHEContext,
               sk: openfhe.LWEPrivateKey,
               log: IO | None = None,
               sample_count: int = 5):
    self.cc = cc
    self.sk = sk
    self.iter = sample_count
    self.log_out = log

  def log(self, s: str):
    if self.log_out is not None:
      print(s, file=self.log_out)

  def run(self) -> CalibrationData:
    data = CalibrationData()

    def measure(e: Event):
      self.log(f"Measuring {e}")
      def logtime(t):
        self.log(f" [{format_ns(t)}]")

      return RuntimeSample(e, data, on_exit=logtime)

    for i in range(0, self.iter):
      ct1 = None
      
      with measure(Event(EventKind.ENCRYPT)):
        ct1 = self.cc.Encrypt(self.sk, 1)

      with measure(Event(EventKind.DECRYPT)):
        self.cc.Decrypt(self.sk, ct1)

      ct2 = self.cc.Encrypt(self.sk, 0)

      for (gate, event) in Calibration.bingate_to_event.items():
        with measure(event):
          self.cc.EvalBinGate(gate, ct1, ct2)

      with measure(Event(EventKind.EVAL_NOT)):
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