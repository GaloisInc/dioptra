from unittest import TestCase
import unittest
import openfhe
import contexts

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
    return PlainWire(self.wire and other.wire)

  def __or__(self, other: 'PlainWire') -> 'PlainWire':
    return PlainWire(self.wire or other.wire)

  def __xor__(self, other: 'PlainWire') -> 'PlainWire':
    return PlainWire(self.wire ^ other.wire)


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

  def zero(self) -> Wire:
    return self.wires[0] & -self.wires[0]

  def one(self) -> Wire:
    return self.wires[0] | -self.wires[0]

  def lt(self, other: 'Circuit') -> Wire:
    assert len(self.wires) == len(other.wires)
    is_lt = self.zero()
    for i in range(0, len(self.wires)):
      w_i = self.wires[i]
      o_i = other.wires[i]
      bit_lt = (-w_i & o_i)
      is_lt =  bit_lt | (w_i.eq(o_i) & is_lt)

    return is_lt

class TestImpl(TestCase):

  def setUp(self) -> None:
    (cc, sk) = contexts.binfhe1()
    self.binenc = BinFHEEncoder(cc, sk)
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
        self.assertEqual(b1.wire and b2.wire, enc.decode_bit(b1 & b2))
        self.assertEqual(b1.wire or b2.wire, enc.decode_bit(b1 | b2))
        self.assertEqual(b1.wire ^ b2.wire, enc.decode_bit(b1 ^ b2))

  def enc_dec(self, enc: Encoder):
    for i in [0,1,5,27,89,124]:
      r = enc.decode_int(enc.encode_int(i, 8))
      self.assertEqual(r, i)

  def test_enc_dec(self):
    self.enc_dec(PlainEncoder())
    self.enc_dec(self.binenc)

  def lt_program(self, enc: Encoder):
    five = (5, enc.encode_int(5, 8))
    ten = (10, enc.encode_int(10, 8))

    for (v1, c1) in [five, ten]:
      for (v2, c2) in [five, ten]:
        self.assertEqual(v1 < v2, enc.decode_bit(c1.lt(c2)))

  def test_lt(self):
    self.lt_program(PlainEncoder())
    self.lt_program(self.binenc)

if __name__ == '__main__':
    unittest.main()
