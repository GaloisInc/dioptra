import os
import openfhe
import time
from typing import IO, Any, Callable, Iterator, TextIO
import random
import enum
import json
import sys

def format_ns(ns: int) -> str:
  micro = ns // 1000
  milli = micro // 1000
  second = milli // 1000

  tstr = f"{ns % 1000:03}n"
  if micro > 0:
    tstr = f"{micro%1000:03}u" + tstr
  if milli > 0:
    tstr = f"{milli%1000:03}m" + tstr
  if second > 0:
    tstr = f"{second}s" + tstr

  return tstr

# range function with step that always includes endpoints
def ep_range(start: int, end: int, step: int) -> Iterator[int]:
  i = start
  while i < end - 1:
    yield i
    i += step

  yield end - 1


class EventKind(enum.Enum):
  ENCODE = 1
  DECODE = 2
  ENCRYPT = 3
  DECRYPT = 4
  EVAL_MULT = 5
  EVAL_ADD = 6
  EVAL_SUB = 7
  EVAL_BOOTSTRAP = 8

class Event:
  def __init__(self, kind: EventKind, arg_depth1: int | None = None, arg_depth2: int | None = None):
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
      raise(f"No runtime found for event: kind:{e.kind} depth 1:{e.arg_depth1} depth 2:{e.arg_depth2}")

class RuntimeSamples:
  def __init__(self):
    self.samples: dict[Event, list[int]] = {}

  def add_sample(self, e: Event, ns: int) -> None:
    if e not in self.samples:
      self.samples[e] = []

    self.samples[e].append(ns)

  def write_json(self, f: str):
    lst = [(self.event_to_dict(evt), ts) for (evt, ts) in self.samples.items()]
    with open(f, "w") as fh:
      json.dump(lst, fh)

  def read_json(self, f: str):
    with open(f, "r") as fh:
      lst = [(self.event_from_dict(evt), ts) for (evt, ts) in json.load(fh)]
      self.samples = dict(lst)

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
      return  isinstance(value, RuntimeSamples) and \
              k in self.samples and k in value.samples and \
              sorted(self.samples[k]) == value.samples[k]

    return isinstance(value, RuntimeSamples) and \
           all(key_eq(k) for k in self.samples.keys()) and \
           all(key_eq(k) for k in value.samples.keys())

class RuntimeSample:
  def __init__(self, label: Event, samples: RuntimeSamples, on_exit: Callable[[int], None] | None = None) -> None:
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
    params: openfhe.CCParamsBFVRNS | openfhe.CCParamsBGVRNS | openfhe.CCParamsCKKSRNS, 
    out: TextIO | None = None,
    sample_count: int = 5,
  ) -> None:
    self.params = params
    self.out = out
    self.sample_count = sample_count

  def log(self, msg: str) -> None:
    if self.out is not None:
      print(msg, file=self.out)

  def num_slots(self) -> int:
    assert self.params.GetRingDim().bit_count() == 1, "CKKS ring dimension should be a power of 2"
    return self.params.GetRingDim() >> 1
  
  def calibrate_ckks(self) -> RuntimeSamples:
    self.log("Scheme: CKKS")

    samples = RuntimeSamples()
    def measure(label: EventKind, a1: int | None = None, a2: int | None = None):
      if a1 is None and a2 is None:
        self.log(f"Measuring {label}")

      elif a2 is None:
        self.log(f"Measuring {label} depth={a1}")

      else:
        self.log(f"Measuring {label} depth1={a1} depth2={a2}")
      
      def on_exit(ns: int):
        self.log(f"   [{format_ns(ns)}]")

      return RuntimeSample(Event(label, a1, a2), samples, on_exit=on_exit)

    cc = openfhe.GenCryptoContext(self.params)
    cc.Enable(openfhe.PKESchemeFeature.PKE)
    cc.Enable(openfhe.PKESchemeFeature.KEYSWITCH)
    cc.Enable(openfhe.PKESchemeFeature.LEVELEDSHE)
    cc.Enable(openfhe.PKESchemeFeature.ADVANCEDSHE)
    cc.Enable(openfhe.PKESchemeFeature.FHE)

    self.log("Generating evaluation keys...")

    # TODO: make these configurable
    level_budget = [3, 3]
    bsgs_dim = [0,0]
    cc.EvalBootstrapSetup(level_budget, bsgs_dim, self.num_slots())

    # key generation
    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)
    cc.EvalBootstrapKeyGen(key_pair.secretKey, self.num_slots())
  
    max_mult_depth = self.params.GetMultiplicativeDepth()
    
    # an arbitrary plaintext
    pt_val = [0] * self.num_slots()
    
    for iteration in range(0, self.sample_count):
      self.log(f"Iteration {iteration}")

      pt = cc.MakeCKKSPackedPlaintext(pt_val, slots=self.num_slots())
      ct = cc.Encrypt(key_pair.publicKey, pt)
      with measure(EventKind.EVAL_BOOTSTRAP):
        cc.EvalBootstrap(ct)

      ct_by_depth = []
      for depth in range(0, max_mult_depth):
        with measure(EventKind.ENCODE, depth):
          pt = cc.MakeCKKSPackedPlaintext(pt_val, slots=self.num_slots(), level=depth)

        with measure(EventKind.ENCRYPT, depth):
          ct = cc.Encrypt(key_pair.publicKey, pt)

        with measure(EventKind.DECRYPT, depth):
          cc.Decrypt(key_pair.secretKey, ct)

        with measure(EventKind.DECODE, depth):
          pt.GetRealPackedValue()

        ct_by_depth.append(ct)

      for depth1 in range(0, max_mult_depth):
        for depth2 in range(depth1, max_mult_depth):
          with measure(EventKind.EVAL_ADD, depth1, depth2):
            cc.EvalAdd(ct_by_depth[depth1], ct_by_depth[depth2])

          with measure(EventKind.EVAL_MULT, depth1, depth2):
            cc.EvalMult(ct_by_depth[depth1], ct_by_depth[depth2])

          with measure(EventKind.EVAL_SUB, depth1, depth2):
            cc.EvalSub(ct_by_depth[depth1], ct_by_depth[depth2])

    return samples
  
  def calibrate(self) -> RuntimeSamples:
    self.log("Beginning calibration...")
    if isinstance(self.params, openfhe.CCParamsCKKSRNS):
      return self.calibrate_ckks()

    raise NotImplementedError(f"Scheme not implemented in calibration: {type(self.params)}")


def run_example():
  # Setup Parameters
  parameters = openfhe.CCParamsCKKSRNS()
  secret_key_dist = openfhe.SecretKeyDist.UNIFORM_TERNARY
  parameters.SetSecretKeyDist(secret_key_dist)
  parameters.SetSecurityLevel(openfhe.SecurityLevel.HEStd_NotSet)
  parameters.SetRingDim(1 << 16)

  rescale_tech = openfhe.ScalingTechnique.FLEXIBLEAUTO

  dcrt_bits = 59
  first_mod = 60

  parameters.SetScalingModSize(dcrt_bits)
  parameters.SetScalingTechnique(rescale_tech)
  parameters.SetFirstModSize(first_mod)

  num_iterations = 2

  level_budget = [3, 3]
  depth = 10 + openfhe.FHECKKSRNS.GetBootstrapDepth(level_budget, secret_key_dist) + (num_iterations - 1)

  parameters.SetMultiplicativeDepth(depth)
  c = Calibration(parameters, sys.stdout, sample_count=1)
  samples = c.calibrate()
  samples.write_json("balanced.samples")
  s = RuntimeSamples()
  s.read_json("balanced.samples")
  assert s == samples






# def call_with_time(f, *args, **kwargs):
#   begin = time.process_time_ns()
#   result = f(*args, **kwargs)
#   end = time.process_time_ns()
#   return (result, end - begin)


# def mk_fresh_plaintext(cc: openfhe.CryptoContext) -> openfhe.Plaintext:
#   x = [random.uniform(0, 1) for i in range(num_slots)]
#   x_pt = cryptocontext.MakeCKKSPackedPlaintext(x)
#   x_pt.SetLength(num_slots)
#   return x_pt


# def mk_fresh_ciphertext(cc: openfhe.CryptoContext, key: openfhe.PublicKey) -> openfhe.Ciphertext:
#   return cc.Encrypt(key, mk_fresh_plaintext(cc))


# stats: list[tuple[str, int, int, int]] = []
# def record(ct: openfhe.Ciphertext, label: str, t: int = 0):
#     stats.append((label, ct.GetLevel(), ct.GetSlots(), t))
#     return ct

# def time_ct(desc: str, f, *args, **kwargs) -> openfhe.Ciphertext:
#    (ct, t) = call_with_time(f, *args, **kwargs)
#    return record(ct, desc, t)

# # Setup Parameters
# parameters = openfhe.CCParamsCKKSRNS()
# secret_key_dist = openfhe.SecretKeyDist.UNIFORM_TERNARY
# parameters.SetSecretKeyDist(secret_key_dist)
# parameters.SetSecurityLevel(openfhe.SecurityLevel.HEStd_NotSet)
# parameters.SetRingDim(1 << 16)

# rescale_tech = openfhe.ScalingTechnique.FLEXIBLEAUTO

# dcrt_bits = 59
# first_mod = 60

# parameters.SetScalingModSize(dcrt_bits)
# parameters.SetScalingTechnique(rescale_tech)
# parameters.SetFirstModSize(first_mod)

# num_iterations = 2

# level_budget = [3, 3]
# bsgs_dim = [0,0]
  
# depth = 10 + openfhe.FHECKKSRNS.GetBootstrapDepth(level_budget, secret_key_dist) + (num_iterations - 1)

# parameters.SetMultiplicativeDepth(depth)

# # Make context and enable features

# cryptocontext = openfhe.GenCryptoContext(parameters)

# cryptocontext.Enable(openfhe.PKESchemeFeature.PKE)
# cryptocontext.Enable(openfhe.PKESchemeFeature.KEYSWITCH)
# cryptocontext.Enable(openfhe.PKESchemeFeature.LEVELEDSHE)
# cryptocontext.Enable(openfhe.PKESchemeFeature.ADVANCEDSHE)
# cryptocontext.Enable(openfhe.PKESchemeFeature.FHE)

# # precomputation of keys

# num_slots = 2**15
# cryptocontext.EvalBootstrapSetup(level_budget, bsgs_dim, num_slots)

# # key generation
# key_pair = cryptocontext.KeyGen()
# cryptocontext.EvalMultKeyGen(key_pair.secretKey)
# cryptocontext.EvalBootstrapKeyGen(key_pair.secretKey, num_slots)


# stats = []

# ct = time_ct("fresh ct", mk_fresh_ciphertext, cryptocontext, key_pair.publicKey)
# cts_by_depth = [ct]
# for i in range(0, depth * 4):
#   print(i)
#   ct = time_ct(f"EvalMult: fresh * depth {i}", cryptocontext.EvalMult, ct,  mk_fresh_ciphertext(cryptocontext, key_pair.publicKey))
#   cts_by_depth.append(ct)

# for i in range(0, depth):
#   for j in range(i, depth):
#       time_ct(f"EvalMult: depth {i} * depth {j}", cryptocontext.EvalMult, cts_by_depth[i], cts_by_depth[j])

# for i in range(0, depth):
#   time_ct(f"EvalBootstrap: {i}", cryptocontext.EvalBootstrap, cts_by_depth[1])

# for (label, levels, slots, t) in stats:
#   print(f"\"{label}\",{levels},{slots},{format_ns(t)}" )