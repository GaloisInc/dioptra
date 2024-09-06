from enum import Enum
from typing import Any, Iterable, Self
import openfhe

class LevelInfo:
  def __init__(self, level: int = 0, noise_scale_deg: int = 1):
    self.noise_scale_deg = noise_scale_deg # rename to is mul result?
    self.level = level

  def __hash__(self) -> int:
    return hash((self.noise_scale_deg, self.level))
  
  def __eq__(self, value: object) -> bool:
    return isinstance(value, LevelInfo) \
       and self.noise_scale_deg == value.noise_scale_deg \
       and self.level == value.level
  
  def levelled_incr(self) -> 'LevelInfo':
    if self.noise_scale_deg < 2:
      return LevelInfo(self.level, self.noise_scale_deg + 1)
    else:
      return LevelInfo(self.level + 1, self.noise_scale_deg)
    
  def max(self, other: 'LevelInfo') -> 'LevelInfo':
    if self.level < other.level or (self.level == other.level and self.noise_scale_deg < other.noise_scale_deg):
      return other
    
    return self
  
  def to_dict(self) -> dict[str, Any]:
    return {
      "noise_scale_deg": self.noise_scale_deg,
      "level": self.level
    }
  
  @staticmethod
  def from_dict(d: dict[str, Any]) -> 'LevelInfo':
    return LevelInfo(level=d["level"], noise_scale_deg=d["noise_scale_deg"])
  
  def __str__(self):
    return f"LevelInfo(level={self.level}, noise_scale_deg={self.noise_scale_deg})"
  
  
class SchemeModelPke:
  """This class encodes information about different PKE schemes"""
  def __init__(self, name: str) -> None:
    self.name = name

  def min_level(self) -> LevelInfo:
    raise NotImplementedError(f"scheme '{self.name}' does not implement `min_level`")
  
  def mul_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    raise NotImplementedError(f"scheme '{self.name}' does not implement `mul_level`")
  
  def add_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    raise NotImplementedError(f"scheme '{self.name}' does not implement `add_level`")
  
  def num_slots(self, cc: openfhe.CryptoContext) -> int:
    raise NotImplementedError(f"scheme '{self.name}' does not implement `num_slots`")

  def arbitrary_pt(self, cc: openfhe.CryptoContext, level: LevelInfo) -> openfhe.Plaintext:
    raise NotImplementedError(f"scheme '{self.name}' does not implement `arbitrary_ct`")

  def arbitrary_ct(self, cc: openfhe.CryptoContext, sk: openfhe.PublicKey, level: LevelInfo) -> openfhe.Ciphertext:
    return cc.Encrypt(sk, self.arbitrary_pt(cc, level))
  
  
class SchemeModelCKKS(SchemeModelPke):
  def __init__(self):
    super().__init__("CKKS")

  def min_level(self) -> LevelInfo:
    return LevelInfo(0, 1)
  
  def mul_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    return lev1.max(lev2).levelled_incr()
  
  def add_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    return lev1.max(lev2)
  
  def num_slots(self, cc: openfhe.CryptoContext) -> int:
    return cc.GetRingDimension() // 2
  
  def arbitrary_pt(self, cc: openfhe.CryptoContext, level: LevelInfo) -> openfhe.Ciphertext:
    return cc.MakeCKKSPackedPlaintext([0] * self.num_slots(cc), level=level.level, noiseScaleDeg=level.noise_scale_deg)
  
class SchemeModelBGV(SchemeModelPke):
  def __init__(self):
    super().__init__("BGV")

  def min_level(self) -> LevelInfo:
    return LevelInfo(0, 2)
  
  def mul_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    return lev1.max(lev2).levelled_incr()
  
  def add_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    return lev1.max(lev2)
  
  def num_slots(self, cc: openfhe.CryptoContext) -> int:
    return cc.GetRingDimension()
  
  def arbitrary_pt(self, cc: openfhe.CryptoContext, level: LevelInfo) -> openfhe.Ciphertext:
    return cc.MakePackedPlaintext([0] * self.num_slots(cc), level=level.level, noiseScaleDeg=level.noise_scale_deg)
  
class SchemeModelBFV(SchemeModelPke):
  def __init__(self):
    super().__init__("BFV")

  def min_level(self) -> LevelInfo:
    return LevelInfo(0, 1)
  
  def mul_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    mx = lev1.max(lev2)
    return LevelInfo(mx.level, mx.noise_scale_deg + 1)
  
  def add_level(self, lev1: LevelInfo, lev2: LevelInfo) -> LevelInfo:
    return lev1.max(lev2)
  
  def num_slots(self, cc: openfhe.CryptoContext) -> int:
    return cc.GetRingDimension()
  
  def arbitrary_pt(self, cc: openfhe.CryptoContext, level: LevelInfo) -> openfhe.Ciphertext:
    return cc.MakePackedPlaintext([0] * self.num_slots(cc), level=level.level, noiseScaleDeg=level.noise_scale_deg)


class PkeSchemeModels():
  CKKS = SchemeModelCKKS()
  BGV = SchemeModelBGV()
  BFV = SchemeModelBFV()

  @staticmethod
  def scheme_model_for(params: openfhe.CCParamsBFVRNS | openfhe.CCParamsBGVRNS | openfhe.CCParamsCKKSRNS) -> SchemeModelPke:
    if isinstance(params, openfhe.CCParamsBFVRNS):
      return PkeSchemeModels.BFV
    
    elif isinstance(params, openfhe.CCParamsBGVRNS):
      return PkeSchemeModels.BGV
    
    elif isinstance(params, openfhe.CCParamsCKKSRNS):
      return PkeSchemeModels.CKKS
    
    raise NotImplementedError(f"scheme_model_for {type(params)}")
