import time
from typing import IO, Any, Callable
import openfhe

from dioptra.analyzer.binfhe.event import Event, EventKind
from dioptra.analyzer.utils.util import format_ns

class CalibrationData:
  def __init__(self):
    self.runtime_samples : dict[Event, list[int]]

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
    openfhe.BINGATE.XNOR: Event(EventKind.EVAL_BIN_GATE_XNOR)
  }

  def __init__(self, 
               cc: openfhe.BinFHEContext,
               sk: openfhe.LWEPrivateKey,
               iter: int = 5,
               log: IO | None = None):
    self.cc = cc
    self.sk = sk
    self.iter = iter
    self.log_out = log

  def log(self, s: str):
    if self.log_out is not None:
      print(s, file=self.log_out)

  def run(self) -> CalibrationData:
    data = CalibrationData()

    def measure(e: Event):
      self.log(f"Measuring {e}")
      def exit(t):
        self.log(f" [{format_ns(t)}]")

      return RuntimeSample(e, data)

    for i in range(0, self.iter):
      ct1 = self.cc.Encrypt(self.sk, 1)
      ct2 = self.cc.Encrypt(self.sk, 0)

      for gate in openfhe.BINGATE:
        if gate not in Calibration.bingate_to_event:
          raise ValueError(f"unsupported gate {gate.name}")
        
        with measure(Calibration.bingate_to_event[gate]):
          self.cc.EvalBinGate(gate, ct1, ct2)

    return data