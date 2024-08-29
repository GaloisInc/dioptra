from typing import Iterator
from unittest import TestCase, TestSuite
from dioptra.analyzer.ct_level import CiphertextLevel, PkeSchemeName
from tests.test_contexts import ckks1

class TestCiphertextLevel_CKKS(TestCase):
  @classmethod
  def setUpClass(cls) -> None:
    (cc, params, key, _) = ckks1()
    cls._cc = cc
    cls._key_pair = key
    cls._parameters = params

  def cc(self):
    return TestCiphertextLevel_CKKS._cc
  
  def key_pair(self):
    return TestCiphertextLevel_CKKS._key_pair
  
  def params(self):
    return TestCiphertextLevel_CKKS._parameters
  
  def mkct(self, lv: CiphertextLevel):
    slots = PkeSchemeName.CKKS.num_slots(self.cc())
    vec = [0] * slots

    pt = self.cc().MakeCKKSPackedPlaintext(vec, level=lv.level)
    ct0 = self.cc().Encrypt(self.key_pair().publicKey, pt)
    if lv.noise_scale_deg == 0:
      return ct0
    else:
      return self.cc().EvalMult(ct0, ct0)

    
  def all_levels(self) -> Iterator[CiphertextLevel]:
    for level in range(0, self.params().GetMultiplicativeDepth()):
      for noise_scale_deg in [0,1]:
        yield CiphertextLevel(level=level, noise_scale_deg=noise_scale_deg)

  def test_mul_level(self):
    for ct1 in self.all_levels():
      for ct2 in self.all_levels():
        elev = PkeSchemeName.CKKS.mul_level(ct1, ct2)
        result = self.cc().EvalMult(self.mkct(ct1), self.mkct(ct2))
        self.assertEqual(elev.level, result.GetLevel(), f"l1: [{ct1}] l2: [{ct2}] est: [{elev}] actual level: {result.GetLevel()}")

