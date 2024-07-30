import openfhe
import time
from typing import Any, Iterator, TextIO
import random
import enum
import json
import sys

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
  

class RuntimeSamples:
  def __init__(self, samples: list[tuple[Event, int]]):
    self.samples = samples

class RuntimeSample:
  def __init__(self, label: Event, samples: list[tuple[Event, int]]) -> None:
    self.label = label
    self.samples = samples

  def __enter__(self):
    self.begin = time.process_time_ns()

  def __exit__(self, exc_type, exc_value, traceback):
    end = time.process_time_ns()
    self.samples.append((self.label, end - self.begin))


class Calibration:
  def __init__(self, 
    params: openfhe.CCParamsBFVRNS | openfhe.CCParamsBGVRNS | openfhe.CCParamsCKKSRNS, 
    out: TextIO | None = None,
    sample_count: int = 5,
    depth_interval: int = 1,
  ) -> None:
    self.params = params
    self.out = out
    self.sample_count = sample_count
    self.depth_interval = depth_interval

  def log(self, msg: str) -> None:
    if self.out is not None:
      print(msg, file=self.out)

  def num_slots(self) -> int:
    assert self.params.GetRingDim().bit_count() == 1, "CKKS ring dimension should be a power of 2"
    return self.params.GetRingDim() >> 1
  
  def calibrate_ckks(self) -> RuntimeSamples:
    self.log("Scheme: CKKS")



    samples: list[tuple[Event, int]] = []
    def measure(label: EventKind, a1: int | None = None, a2: int | None = None):
      if a1 is None and a2 is None:
        self.log(f"Measuring {label}")

      elif a2 is None:
        self.log(f"Measuring {label} depth={a1}")

      else:
        self.log(f"Measuring {label} depth1={a1} depth2={a2}")
      
      return RuntimeSample(Event(label, a1, a2), samples)

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

      ct_by_depth = []
      for depth in ep_range(0, max_mult_depth, self.depth_interval):
        with measure(EventKind.ENCODE, depth):
          pt = cc.MakeCKKSPackedPlaintext(pt_val, slots=self.num_slots(), level=depth)

        with measure(EventKind.ENCRYPT, depth):
          ct = cc.Encrypt(key_pair.publicKey, pt)

        with measure(EventKind.DECRYPT, depth):
          cc.Decrypt(key_pair.secretKey, ct)

        with measure(EventKind.DECODE, depth):
          pt.GetRealPackedValue()

        with measure(EventKind.EVAL_BOOTSTRAP, depth):
          cc.EvalBootstrap(ct)

        ct_by_depth.append(ct)

      for depth1 in ep_range(0, max_mult_depth, self.depth_interval):
        for depth2 in ep_range(depth1, max_mult_depth, self.depth_interval):
          with measure(EventKind.EVAL_ADD, depth1, depth2):
            cc.EvalAdd(ct_by_depth[depth1], ct_by_depth[depth2])

          with measure(EventKind.EVAL_MULT, depth1, depth2):
            cc.EvalMult(ct_by_depth[depth1], ct_by_depth[depth2])

          with measure(EventKind.EVAL_SUB, depth1, depth2):
            cc.EvalSub(ct_by_depth[depth1], ct_by_depth[depth2])

    return RuntimeSamples(samples)
  
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
  c = Calibration(parameters, sys.stdout, depth_interval=5)
  samples = c.calibrate()


run_example()



# def format_ns(ns: int) -> str:
#   micro = ns // 1000
#   milli = micro // 1000
#   second = milli // 1000

#   tstr = f"{ns % 1000}n"
#   if micro > 0:
#     tstr = f"{micro%1000}u" + tstr
#   if milli > 0:
#     tstr = f"{milli%1000}m" + tstr
#   if second > 0:
#     tstr = f"{second}s" + tstr

#   return tstr

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