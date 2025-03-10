import os
from typing import Callable
from unittest import TestCase
import unittest
from xmlrpc.client import Boolean
import openfhe

class Encoder:
  def encode_bit(self, bit: bool) -> 'Wire':
    raise NotImplementedError("encode_bit")

  def decode_bit(self, wire: 'Wire') -> bool:
    raise NotImplementedError("decode_bit")

  def encode_int(self, i: int, sz: int) -> 'Circuit':
    bits = []
    s = i
    for _ in range(0, sz):
      bits.append(self.encode_bit(s & 1 == 1))
      s = s >> 1
    
    return Circuit(bits)

  def decode_int(self, c: 'Circuit') -> int:
    v = 0
    for i in range(0, len(c.wires)):
      if self.decode_bit(c.wires[i]):
        v += 1 << i

    return v

class Wire:
  def __neg__(self) -> 'Wire':
    raise NotImplementedError("__neg__")

  def __and__(self, other: 'Wire') -> 'Wire':
    raise NotImplementedError("__and__")

  def __or__(self, other: 'Wire') -> 'Wire':
    raise NotImplementedError("__or__")

  def __xor__(self, other: 'Wire') -> 'Wire':
    raise NotImplementedError("__xor__")

  def adc(self, other: 'Wire') -> tuple['Wire', 'Wire']:
    return (self ^ other, self & other)

  def eq(self, other: 'Wire') -> 'Wire':
    return -(self ^ other)
  
  def cond(self, then: 'Circuit', els: 'Circuit') -> 'Circuit':
    assert(len(then.wires) == len(els.wires))
    return Circuit(list((self & thenwire) | (-(self & elswire)) 
                          for (thenwire,elswire) in zip(then.wires,els.wires)))
  
  # return a zero wire of the same type as this wire
  def zero(self) -> 'Wire':
    return self & -self
    
  def one(self) -> 'Wire':
    return self | -self
  
# --- pt version ----------------------------------------------------------

class PlainEncoder(Encoder):
  def encode_bit(self, bit: bool) -> Wire:
    return PlainWire(bit)

  def decode_bit(self, wire: Wire) -> bool:
    assert isinstance(wire, PlainWire)
    return wire.wire

class PlainWire(Wire):
  def __init__(self, b: bool):
    self.wire = b

  def __neg__(self) -> 'PlainWire':
    return PlainWire(not self.wire)

  def __and__(self, other: 'PlainWire') -> 'PlainWire':
    return PlainWire(self.wire & other.wire)

  def __or__(self, other: 'PlainWire') -> 'PlainWire':
    return PlainWire(self.wire | other.wire)

  def __xor__(self, other: 'PlainWire') -> 'PlainWire':
    return PlainWire(self.wire ^ other.wire)
  
  def zero(self) -> 'PlainWire':
    return PlainWire(False)
  
  def one(self) -> 'PlainWire':
    return PlainWire(True)


# --- binfhe version ----------------------------------------------------------
class BinFHEEncoder(Encoder):
  def __init__(self, cc: openfhe.BinFHEContext, sk: openfhe.PrivateKey):
    self.cc = cc
    self.sk = sk

  def encode_bit(self, bit: bool) -> Wire:
      return BinFHEWire(self.cc, self.cc.Encrypt(self.sk, int(bit)))

  def decode_bit(self, wire: Wire) -> bool:
    assert isinstance(wire, BinFHEWire)
    return self.cc.Decrypt(self.sk, wire.wire) != 0

class BinFHEWire(Wire):
  zerowire: 'BinFHEWire|None' = None
  onewire: 'BinFHEWire|None' = None

  def __init__(self, cc: openfhe.BinFHEContext, l: openfhe.LWECiphertext):
    self.cc = cc
    self.wire = l

  def __neg__(self) -> 'BinFHEWire':
    return BinFHEWire(self.cc, self.cc.EvalNOT(self.wire))

  def __and__(self, other: 'BinFHEWire') -> 'BinFHEWire':
    if self == other:
      return self.wire

    return BinFHEWire(self.cc, self.cc.EvalBinGate(openfhe.AND, self.wire, other.wire))

  def __or__(self, other: 'BinFHEWire') -> 'BinFHEWire':
    if self == other:
      return self.wire

    return BinFHEWire(self.cc, self.cc.EvalBinGate(openfhe.OR, self.wire, other.wire))

  def __xor__(self, other: 'BinFHEWire') -> 'BinFHEWire':
    if self == other:
      return -self

    return BinFHEWire(self.cc, self.cc.EvalBinGate(openfhe.XOR, self.wire, other.wire))
  

# -- circuits -----------------------------------------------------------------

class Circuit:
  def __init__(self, wires: list[Wire]):
    assert(len(wires) > 0)
    self.wires = wires
    self.onewire = None
    self.zerowire = None

  def derive_circuit(self, wires: list[Wire]) -> 'Circuit':
    assert(len(wires) > 0)
    circuit = Circuit(wires)
    circuit.zerowire = self.zerowire
    circuit.onewire = self.onewire
    return circuit

  def zero(self) -> Wire:
    if self.zerowire is None:
      self.zerowire = self.wires[0] & -self.wires[0]
    
    return self.zerowire
  
  def one(self) -> Wire:
    if self.onewire is None:
      self.onewire = self.wires[0] | -self.wires[0]
    
    return self.onewire

  def lt(self, other: 'Circuit') -> Wire:
    assert len(self.wires) == len(other.wires)
    is_lt = None
    for (w_i, o_i) in zip(self.wires, other.wires):
      bit_lt = (-w_i & o_i)
      if is_lt is None:
        is_lt = bit_lt
      else:
        is_lt = bit_lt | (w_i.eq(o_i) & is_lt)

    assert(is_lt is not None)
    return is_lt
  
  def eq(self, other: 'Circuit') -> Wire:
    assert len(self.wires) == len(other.wires)
    result = None
    for (w_i, o_i) in zip(self.wires, other.wires):
      if result is None:
        result = w_i.eq(o_i)
      else:
        result = w_i.eq(o_i) & result
    
    assert(result is not None)
    return result
  
  def __add__(self, other: 'Circuit') -> 'Circuit':
    assert len(self.wires) == len(other.wires)
    wires = []
    carry_in = self.zero()
    for i in range(0, len(self.wires)):
      (b, carry_out) = self.wires[i].adc(other.wires[i])
      wires.append(b | carry_in)
      carry_in = carry_out

    return self.derive_circuit(wires)
  
  def __rshift__(self, shift: int) -> 'Circuit':
    wires = []
    z = self.zero()
    for i in range(0, len(self.wires)):
      val = self.wires[i + shift] if i + shift < len(self.wires) else z
      wires.append(val)

    return Circuit(wires)
  
  def __lshift__(self, shift: int) -> 'Circuit':
    wires = []
    z = self.zero()
    for i in range(0, len(self.wires)):
      val = self.wires[i - shift] if i - shift >= 0 else z
      wires.append(val)

    return self.derive_circuit(wires)
  
  def __mul__(self, other: 'Circuit') -> 'Circuit':
    assert(len(self.wires) == len(other.wires))
    z = self.zero()
    result = self.derive_circuit(list(z for _ in self.wires))

    for i in range(0, len(self.wires)):
      w = other.wires[i]
      addend = []
      for j in range(0, len(self.wires)):
        addend.append(self.wires[j - i] & w if j - i >= 0 else z)
      
      result = result + self.derive_circuit(addend)

    return result
  
      
class TestImpl(TestCase):
  def setUp(self) -> None:
    self.encs: list[Encoder] = [PlainEncoder()]

    if os.environ.get("CIRCUIT_TEST_FHE", "0") == "1":
      cc = openfhe.BinFHEContext()
      cc.GenerateBinFHEContext(openfhe.STD128, openfhe.GINX)
      sk = cc.KeyGen()
      cc.BTKeyGen(sk)

      self.encs.append(BinFHEEncoder(cc, sk))

    return super().setUp()

  def test_validate_plain(self):
    enc = PlainEncoder()
    t = enc.encode_bit(True)
    f = enc.encode_bit(False)
    assert isinstance(t, PlainWire)
    assert isinstance(f, PlainWire)

    self.assertTrue(enc.decode_bit(t))
    self.assertFalse(enc.decode_bit(f))
    
    for b1 in [t, f]:
      self.assertEqual(not b1.wire, enc.decode_bit(-b1))

      for b2 in [t, f]:
        self.assertEqual(b1.wire & b2.wire, enc.decode_bit(b1 & b2))
        self.assertEqual(b1.wire | b2.wire, enc.decode_bit(b1 | b2))
        self.assertEqual(b1.wire ^ b2.wire, enc.decode_bit(b1 ^ b2))
        self.assertEqual(b1.wire == b2.wire, enc.decode_bit(b1.eq(b2)))

  def run_program(self, f: Callable[[Encoder], None]):
    for enc in self.encs:
      f(enc)

  def enc_dec(self, enc: Encoder):
    for i in [0,1,5,27,89,124]:
      r = enc.decode_int(enc.encode_int(i, 8))
      self.assertEqual(r, i)

  def lt_program(self, enc: Encoder):
    five = (5, enc.encode_int(5, 8))
    ten = (10, enc.encode_int(10, 8))

    for (v1, c1) in [five, ten]:
      for (v2, c2) in [five, ten]:
        self.assertEqual(v1 < v2, enc.decode_bit(c1.lt(c2)))

  def eq_program(self, enc: Encoder):
    five = (5, enc.encode_int(5, 8))
    ten = (10, enc.encode_int(10, 8))

    for (v1, c1) in [five, ten]:
      for (v2, c2) in [five, ten]:
        self.assertEqual(v1 == v2, enc.decode_bit(c1.eq(c2)))


  def add_program(self, enc: Encoder):
    five = enc.encode_int(5, 8)
    ten = enc.encode_int(10, 8)
    self.assertEqual(5 + 10, enc.decode_int(five + ten))

  def lsl_program(self, enc: Encoder):
    ten = enc.encode_int(10, 8)
    self.assertEqual(10 << 2, enc.decode_int(ten << 2))

  def lsr_program(self, enc: Encoder):
    ten = enc.encode_int(10, 8)
    self.assertEqual(10 >> 2, enc.decode_int(ten >> 2))

  def mul_program(self, enc: Encoder):
    v5 = enc.encode_int(5, 8)
    v10 = enc.encode_int(10, 8)
    v254 = enc.encode_int(254, 8)
    self.assertEqual(5 * 10, enc.decode_int(v5 * v10))
    self.assertEqual((254 * 10) % 2**8, enc.decode_int(v254 * v10))

  def test_enc_dec(self):
    self.run_program(self.enc_dec)

  def test_lt(self):
    self.run_program(self.lt_program)

  def test_add(self):
    self.run_program(self.add_program)

  def test_lsr(self):
    self.run_program(self.lsl_program)

  def test_lsl(self):
    self.run_program(self.lsr_program)

  def test_mul(self):
    self.run_program(self.mul_program)

  def test_eq(self):
    self.run_program(self.eq_program)

if __name__ == '__main__':
    unittest.main()
