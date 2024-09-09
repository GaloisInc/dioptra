from typing import Callable
from dioptra.analyzer.binfhe.value import LWECiphertext, LWEPrivateKey
import openfhe

from dioptra.analyzer.metrics.analysisbase import PrivateKey

# TODO: figure out plaintext modulus
class BinFHEAnalyzer:
  def __init__(self, n: int, q: int, beta: int):
    self.n = n
    self.q = q
    self.beta = beta

  def BTKeyGen(self, sk: LWEPrivateKey, keygenMode: openfhe.KEYGEN_MODE = openfhe.KEYGEN_MODE.SYM_ENCRYPT) -> None:
    pass
            
  def Decrypt(self, sk: PrivateKey, ct: LWECiphertext, p: int = 4) -> int:
    return 0 # TODO: value is not correct

  def Encrypt(self, sk: LWEPrivateKey, 
                    m: int, 
                    output: openfhe.BINFHE_OUTPUT = openfhe.BINFHE_OUTPUT.BOOTSTRAPPED, # XXX: TODO
                    p: int = 4, 
                    mod: int = 0) -> LWECiphertext:
    ct = LWECiphertext(length=self.n, modulus=self.q)
    return ct
  
  def _eval_gate_plain(self, gate: openfhe.BINGATE, i1: int, i2: int) -> int:
    if gate == openfhe.BINGATE.OR:
      return i1 | i2
    
    elif gate == openfhe.BINGATE.AND:
      return i1 & i2
    
    elif gate == openfhe.BINGATE.NOR:
      return ~(i1 | i2)
    
    elif gate == openfhe.BINGATE.NAND:
      return ~(i1 & i2)
    
    elif gate == openfhe.BINGATE.XOR_FAST or gate == openfhe.BINGATE.XOR:
      return i1 ^ i2
    
    elif gate == openfhe.BINGATE.XNOR_FAST or gate == openfhe.BINGATE.XNOR:
      return ~(i1 ^ i2)
    
    raise NotImplementedError(f"gate type not implemented: {gate.name}")
    

  def EvalBinGate(self, gate: openfhe.BINGATE, ct1: LWECiphertext, ct2: LWECiphertext) -> LWECiphertext:
    ct = LWECiphertext(length=self.n, modulus=self.q)

    return ct
  
  # TODO: need to figure out how long the resulting list is - ask Hilder
  def EvalDecomp(self, ct: LWECiphertext) -> list[LWECiphertext]:
    raise NotImplemented("EvalDecomp is not implemented")
  
  def EvalFloor(self, ct: LWECiphertext, roundbits: int = 0) -> LWECiphertext:
    ct = LWECiphertext(length=self.n, modulus=self.q)

    return ct
  
  def EvalFunc(self, ct: LWECiphertext, LUT: list[int]) -> LWECiphertext:
    ct = LWECiphertext(ct.length, ct.ct_mod)

    return ct
  
  def EvalNot(self, ct: LWECiphertext) -> LWECiphertext:
    ct = LWECiphertext(ct.length, ct.ct_mod)

    return ct
  
  def EvalSign(self, ct: LWECiphertext) -> LWECiphertext:
    ct = LWECiphertext(ct.length, ct.ct_mod)

    return ct

  def GenerateBinFHEContext(self, *args, **kwargs):
    pass # TODO: we can probably ingore this for now

  def GenerateLUTviaFunction(self, f: Callable[[int, int], int], p: int) -> list[int]:
    return list([])
  
  def GetBeta(self) -> int:
    return self.beta

  def Getn(self) -> int:
    return self.n

  def Getq(self) -> int:
    return self.q
  
  def KeyGen(self) -> LWEPrivateKey:
    return LWEPrivateKey(self.n)




