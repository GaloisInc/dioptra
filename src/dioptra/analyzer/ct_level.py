from enum import Enum
import openfhe

class CiphertextLevel:
  def __init__(self, level: int = 0, noise_scale_deg: int = 0):
    self.noise_scale_deg = noise_scale_deg # rename to is mul result?
    self.level = level

  def __hash__(self) -> int:
    return hash((self.noise_scale_deg, self.level))
  
  def __eq__(self, value: object) -> bool:
    return isinstance(value, CiphertextLevel) \
       and self.noise_scale_deg == value.noise_scale_deg \
       and self.level == value.level
  
  def __str__(self) -> str:
    return f"level: {self.level} noise_scale_deg: {self.noise_scale_deg}"
  
class PkeSchemeName(Enum):
  CKKS = 1
  BGV = 2
  BFV = 3

  def mul_level(self, lev1: CiphertextLevel, lev2: CiphertextLevel) -> CiphertextLevel:
    if self == PkeSchemeName.CKKS or self == PkeSchemeName.BGV:
      return CiphertextLevel(level=max(lev1.level + lev1.noise_scale_deg, lev2.level + lev2.noise_scale_deg), noise_scale_deg=1)

    elif self == PkeSchemeName.BFV:  # in BFV's case, levels must be equivalent
      return lev1
    
    raise NotImplemented(f"Scheme not implemented {self.name}")
  
  def add_level(self, lev1: CiphertextLevel, lev2: CiphertextLevel) -> CiphertextLevel:
    if self == PkeSchemeName.CKKS or self == PkeSchemeName.BGV:
      return CiphertextLevel(level=max(lev1.level + lev1.noise_scale_deg, lev2.level + lev2.noise_scale_deg), noise_scale_deg=0)

    elif self == PkeSchemeName.BFV:  # in BFV's case, levels must be equivalent
      return lev1
    
    raise NotImplemented(f"Scheme not implemented {self.name}")
  def num_slots(self, cc: openfhe.CryptoContext) -> int:
    if self == PkeSchemeName.CKKS:
      return cc.GetRingDimension() // 2
    
    else:
      return cc.GetRingDimension()

    