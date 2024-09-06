import os
import openfhe
import time
from typing import IO, Any, Callable, Iterable, Iterator, TextIO
import random
import enum
import json
import sys

from dioptra.analyzer.scheme import LevelInfo, PkeSchemeModels, SchemeModelPke
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
  commutative_event_kinds = set([
    EventKind.EVAL_ADD_CTCT, EventKind.EVAL_MULT_CTCT, EventKind.EVAL_SUB_CTCT,
    EventKind.EVAL_MULT_CTPT, EventKind.EVAL_ADD_CTPT, EventKind.EVAL_SUB_CTPT
  ])

  def __init__(self, kind: EventKind, arg_level1: LevelInfo | None = None, arg_level2: LevelInfo | None = None):
    self.kind = kind

    # if arg_depth2 is specified, arg_depth1 must be specified as well
    assert arg_level2 is None or arg_level1 is not None
    self.arg_level1 = arg_level1
    self.arg_level2 = arg_level2

  def __eq__(self, value: object) -> bool:
    return isinstance(value, Event) \
           and self.kind == value.kind \
           and self.arg_level1 == value.arg_level1 \
           and self.arg_level2 == value.arg_level2

  def __hash__(self) -> int:
    return hash((self.kind, self.arg_level1, self.arg_level2))
  
  def to_dict(self) -> dict[str, Any]:
    return {
      "kind": self.kind.value,
      "arg_level1": self.arg_level1.to_dict() if self.arg_level1 is not None else None,
      "arg_level2": self.arg_level2.to_dict() if self.arg_level2 is not None else None,
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
  def from_dict(d) -> 'Event':
    e = Event(EventKind.ENCODE)
    e.kind = EventKind(d["kind"])
    e.arg_level1 = LevelInfo.from_dict(d["arg_level1"]) if "arg_level1" in d else None,
    e.arg_level2 = LevelInfo.from_dict(d["arg_level2"]) if "arg_level2" in d else None,
    return e

  
class RuntimeTable:
  def __init__(self, runtimes: dict[Event, int]):
    self.runtimes = runtimes

  def get_runtime_ns(self, e: Event) -> int:
    if e in self.runtimes:
      return self.runtimes[e]
    elif e.arg_level2 is not None and e.is_commutative():
      e_swaped = Event(e.kind, e.arg_level2, e.arg_level1)
      return self.runtimes[e_swaped]
    else:
      raise NotImplementedError(f"No runtime found for event: {e}")

class CalibrationData:
  def __init__(self):
    self.samples: dict[Event, list[int]] = {}

  def add_sample(self, e: Event, ns: int) -> None:
    if e not in self.samples:
      self.samples[e] = []

    self.samples[e].append(ns)

  def to_dict(self) -> dict[str, Any]:
    evts = [(evt.to_dict(), ts) for (evt, ts) in self.samples.items()]
    return {
      "samples": evts,
    }
  
  @staticmethod
  def from_dict(obj: dict[str, Any]) -> 'CalibrationData':
    evts = [(Event.from_dict(evt), ts) for (evt, ts) in obj["samples"]]
    cal = CalibrationData()
    cal.samples = dict(evts)
    return cal

  def write_json(self, f: str):
    with open(f, "w") as fh:
      json.dump(self.to_dict(), fh)

  def read_json(self, f: str):
    with open(f, "r") as fh:
      obj = json.load(fh)
      return CalibrationData.from_dict(obj)

  def avg_runtime_table(self) -> RuntimeTable:
    table = {}
    for (event, runtimes) in self.samples.items():
      table[event] = sum(runtimes) // len(runtimes)

    return RuntimeTable(table)
  
  
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


  def is_ckks(self) -> bool:
    return isinstance(self.params, openfhe.CCParamsCKKSRNS)
  
  def is_bgv(self) -> bool:
    return isinstance(self.params, openfhe.CCParamsBGVRNS)
  
  def is_bfv(self) -> bool:
    return isinstance(self.params, openfhe.CCParamsBFVRNS)
  
  def scheme_model(self) -> SchemeModelPke:
    return PkeSchemeModels.scheme_model_for(self.params)

  def log(self, msg: str) -> None:
    if self.out is not None:
      print(msg, file=self.out)

  def num_slots(self) -> int:
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      assert self.params.GetRingDim().bit_count() == 1, "CKKS ring dimension should be a power of 2"
      return self.params.GetRingDim() >> 1
    else:
      return self.cc.GetRingDimension() ## XXX: ask hilder about this
  
  def encode(self, level: LevelInfo) -> openfhe.Plaintext:
    pt_val = [0] * self.num_slots()
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      return self.cc.MakeCKKSPackedPlaintext(pt_val, slots=self.num_slots(), level=level.level, noiseScaleDeg=level.noise_scale_deg)
    else:
      return self.cc.MakePackedPlaintext(pt_val, level=level.level, noiseScaleDeg=level.noise_scale_deg)
    
  def decode(self, pt: openfhe.Plaintext) -> None:
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      pt.GetRealPackedValue()
    else:
      pt.GetPackedValue()

  def all_levels(self) -> Iterable[LevelInfo]:
    if self.is_ckks():
      for deg in [0, 1]:
        for level in range(0, self.params.GetMultiplicativeDepth()):
          yield LevelInfo(level, deg)

    if self.is_bgv():
      yield LevelInfo(0, 2)
      for deg in [0,1]:
        for level in range(1, self.params.GetMultiplicativeDepth()):
          yield LevelInfo(level, deg)

    # dunno how to think about noise scale deg in this case
    if self.is_bfv():
      for level in range(0, self.params.GetMultiplicativeDepth()):
        yield LevelInfo(level, 0)

  def level_pairs(self) -> Iterable[tuple[LevelInfo, LevelInfo]]:
    if self.is_bfv():
      for l in self.all_levels():
        yield (l,l)

    else:
      for l1 in self.all_levels():
        for l2 in self.all_levels():
          yield (l1, l2)

  def level_pairs_comm(self) -> Iterable[tuple[LevelInfo, LevelInfo]]:
    if self.is_bfv():
      return self.level_pairs()
    
    else:
      all = list(self.all_levels())
      for i in range(0, len(all)):
        for j in range(i, len(all)):
          yield (all[i], all[j])


  def calibrate_base(self) -> CalibrationData:
    samples = CalibrationData()
    def measure(label: EventKind, a1: LevelInfo | None = None, a2: LevelInfo | None = None):
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
    
    for iteration in range(0, self.sample_count):
      self.log(f"Iteration {iteration}")

      # XXX: is this its own function?
      if openfhe.PKESchemeFeature.FHE in self.features and self.is_ckks():
        pt = self.encode(LevelInfo(0, 1))
        ct = cc.Encrypt(key_pair.publicKey, pt)
        with measure(EventKind.EVAL_BOOTSTRAP):
          cc.EvalBootstrap(ct)
        
      for level in self.all_levels():
        with measure(EventKind.ENCODE, level):
          pt = self.encode(level)

        with measure(EventKind.ENCRYPT, level):
          ct = cc.Encrypt(key_pair.publicKey, pt)

        with measure(EventKind.DECRYPT, level):
          cc.Decrypt(key_pair.secretKey, ct)

        with measure(EventKind.DECODE, level):
          self.decode(pt)


      seen = set()
      for (level1, level2) in self.level_pairs_comm():
          pt = self.scheme_model().arbitrary_pt(self.cc, level2)
          ct1 = self.scheme_model().arbitrary_ct(self.cc, self.key_pair.publicKey, level1)
          ct2 = self.scheme_model().arbitrary_ct(self.cc, self.key_pair.publicKey, level2)

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

