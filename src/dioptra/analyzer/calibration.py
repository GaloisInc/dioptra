import os
import openfhe
import time
from typing import IO, Any, Callable, Iterable, Iterator, TextIO
import random
import enum
import json
import sys

from dioptra.analyzer.ct_level import CiphertextLevel
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
  def __init__(self, kind: EventKind, arg_depth1: CiphertextLevel | None = None, arg_depth2: CiphertextLevel | None = None):
    self.kind = kind

    # if arg_depth2 is specified, arg_depth1 must be specified as well
    assert arg_depth2 is None or arg_depth1 is not None
    self.arg_depth1 = arg_depth1
    self.arg_depth2 = arg_depth2

  def __eq__(self, value: object) -> bool:
    return isinstance(value, Event) \
           and self.kind == value.kind \
           and self.arg_depth1 == value.arg_depth1 \
           and self.arg_depth2 == value.arg_depth2

  def __hash__(self) -> int:
    return hash((self.kind, self.arg_depth1, self.arg_depth2))
  
class RuntimeTable:
  def __init__(self, runtimes: dict[Event, int]):
    self.runtimes = runtimes

  def get_runtime_ns(self, e: Event) -> int:
    if e in self.runtimes:
      return self.runtimes[e]
    elif e.arg_depth2 is not None:
      e_swaped = Event(e.kind, e.arg_depth2, e.arg_depth1)
      return self.runtimes[e_swaped]
    else:
      raise NotImplementedError(f"No runtime found for event: kind:{e.kind} depth 1:{e.arg_depth1} depth 2:{e.arg_depth2}")

class CalibrationData:
  def __init__(self):
    self.samples: dict[Event, list[int]] = {}
    self.bootstrap_level: int = 0

  def record_bootstrap_lv(self, out_lv: int) -> None:
    self.bootstrap_level = max(out_lv, self.bootstrap_level)

  def add_sample(self, e: Event, ns: int) -> None:
    if e not in self.samples:
      self.samples[e] = []

    self.samples[e].append(ns)

  def write_json(self, f: str):
    evts = [(self.event_to_dict(evt), ts) for (evt, ts) in self.samples.items()]
    obj = {
      "samples": evts,
      "bootstrap_level": self.bootstrap_level,
    }

    with open(f, "w") as fh:
      json.dump(obj, fh)

  def read_json(self, f: str):
    with open(f, "r") as fh:
      obj = json.load(fh)
      lst = [(self.event_from_dict(evt), ts) for (evt, ts) in obj["samples"]]
      self.samples = dict(lst)
      self.bootstrap_level = obj["bootstrap_level"]

  def avg_runtime_table(self) -> RuntimeTable:
    table = {}
    for (event, runtimes) in self.samples.items():
      table[event] = sum(runtimes) // len(runtimes)

    return RuntimeTable(table)
  
  def event_to_dict(self, e: Event) -> dict[str, Any]:
    r: dict[str, Any] = {"kinddesc": e.kind.name, "kindid": e.kind.value }
    if e.arg_depth1 is not None:
      r["depth1"] = e.arg_depth1

    if e.arg_depth2 is not None:
      r["depth2"] = e.arg_depth2

    return r
  
  def event_from_dict(self, r: dict[str, Any]) -> Event:
    kind = EventKind(r["kindid"])
    depth1 = r.get("depth1", None)
    depth2 = r.get("depth2", None)
    return Event(kind, depth1, depth2)
  
  def __eq__(self, value: object) -> bool:
    def sorted(l: list) -> list:
      s = list(l)
      s.sort()
      return s
    
    def key_eq(k: Event) -> bool:
      return  isinstance(value, CalibrationData) and \
              k in self.samples and k in value.samples and \
              sorted(self.samples[k]) == value.samples[k]

    return isinstance(value, CalibrationData) and \
           all(key_eq(k) for k in self.samples.keys()) and \
           all(key_eq(k) for k in value.samples.keys())

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
    self.samples.add_sample(self.label, t)
    if self.on_exit is not None:
      self.on_exit(t)


class Calibration:
  def __init__(self, 
    cc: openfhe.CryptoContext,
    params: openfhe.CCParamsBFVRNS | openfhe.CCParamsBGVRNS | openfhe.CCParamsCKKSRNS,
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

  def log(self, msg: str) -> None:
    if self.out is not None:
      print(msg, file=self.out)

  def num_slots(self) -> int:
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      assert self.params.GetRingDim().bit_count() == 1, "CKKS ring dimension should be a power of 2"
      return self.params.GetRingDim() >> 1
    else:
      return self.cc.GetRingDimension() ## XXX: ask hilder about this
  
  def encode(self, level) -> openfhe.Plaintext:
    pt_val = [0] * self.num_slots()
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      return self.cc.MakeCKKSPackedPlaintext(pt_val, slots=self.num_slots(), level=level)
    else:
      return self.cc.MakePackedPlaintext(pt_val, level=level)
    
  def decode(self, pt: openfhe.Plaintext) -> None:
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      pt.GetRealPackedValue()
    else:
      pt.GetPackedValue()
  
  def calibrate_base(self) -> CalibrationData:
    samples = CalibrationData()
    def measure(label: EventKind, a1: CiphertextLevel | None = None, a2: CiphertextLevel | None = None):
      if a1 is None and a2 is None:
        self.log(f"Measuring {label}")

      elif a2 is None:
        self.log(f"Measuring {label} depth={a1}")

      else:
        self.log(f"Measuring {label} depth1={a1} depth2={a2}")
      
      def on_exit(ns: int):
        self.log(f"   [{format_ns(ns)}]")

      return RuntimeSample(Event(label, a1, a2), samples, on_exit=on_exit)

    cc = self.cc
    key_pair = self.key_pair

    max_mult_depth = self.params.GetMultiplicativeDepth()
    self.log(f"Max multiplicative depth: {max_mult_depth}")
    self.log(f"Slots: {self.num_slots()}")
    
    for iteration in range(0, self.sample_count):
      self.log(f"Iteration {iteration}")

      # XXX: is this its own function?
      if openfhe.PKESchemeFeature.FHE in self.features:
        pt = self.encode(0)
        ct = cc.Encrypt(key_pair.publicKey, pt)
        ct_bs = None
        with measure(EventKind.EVAL_BOOTSTRAP):
          ct_bs = cc.EvalBootstrap(ct)
        
        samples.record_bootstrap_lv(ct_bs)

      ct_by_depth = []
      pt_by_depth = []
      for level in range(0, max_mult_depth):
        with measure(EventKind.ENCODE, level):
          pt = self.encode(level)

        with measure(EventKind.ENCRYPT, level):
          ct = cc.Encrypt(key_pair.publicKey, pt)

        with measure(EventKind.DECRYPT, level):
          cc.Decrypt(key_pair.secretKey, ct)

        with measure(EventKind.DECODE, level):
          self.decode(pt)

        ct_by_depth.append(ct)
        pt_by_depth.append(pt)

      for depth1 in range(0, max_mult_depth):
        for depth2 in range(depth1, max_mult_depth):
          with measure(EventKind.EVAL_ADD_CTCT, depth1, depth2):
            cc.EvalAdd(ct_by_depth[depth1], ct_by_depth[depth2])

          with measure(EventKind.EVAL_MULT_CTCT, depth1, depth2):
            cc.EvalMult(ct_by_depth[depth1], ct_by_depth[depth2])

          with measure(EventKind.EVAL_SUB_CTCT, depth1, depth2):
            cc.EvalSub(ct_by_depth[depth1], ct_by_depth[depth2])

        for depth2 in range(0, max_mult_depth):
          with measure(EventKind.EVAL_MULT_CTPT, depth1, depth2):
            cc.EvalMult(ct_by_depth[depth1], pt_by_depth[depth2])

          with measure(EventKind.EVAL_ADD_CTPT, depth1, depth2):
            cc.EvalMult(ct_by_depth[depth1], pt_by_depth[depth2])

          with measure(EventKind.EVAL_ADD_CTPT, depth1, depth2):
            cc.EvalSub(ct_by_depth[depth1], pt_by_depth[depth2])

    return samples
  
  def calibrate(self) -> CalibrationData:
    self.log("Beginning calibration...")
    return self.calibrate_base()


# def run_example():
#   # Setup Parameters
#   parameters = openfhe.CCParamsCKKSRNS()
#   secret_key_dist = openfhe.SecretKeyDist.UNIFORM_TERNARY
#   parameters.SetSecretKeyDist(secret_key_dist)
#   parameters.SetSecurityLevel(openfhe.SecurityLevel.HEStd_NotSet)
#   parameters.SetRingDim(1 << 16)

#   rescale_tech = openfhe.ScalingTechnique.FLEXIBLEAUTO

#   dcrt_bits = 59
#   first_mod = 60

#   parameters.SetScalingModSize(dcrt_bits)
#   parameters.SetScalingTechnique(rescale_tech)
#   parameters.SetFirstModSize(first_mod)

#   num_iterations = 2

#   level_budget = [3, 3]
#   depth = 10 + openfhe.FHECKKSRNS.GetBootstrapDepth(level_budget, secret_key_dist) + (num_iterations - 1)

#   parameters.SetMultiplicativeDepth(depth)
  
#   c = Calibration(parameters, sys.stdout, sample_count=1)
#   samples = c.calibrate()
#   samples.write_json("balanced.samples")
#   s = RuntimeSamples()
#   s.read_json("balanced.samples")
#   assert s == samples

