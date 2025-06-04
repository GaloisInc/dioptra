#
# Implementation of simple circuits for BinFHE
#
# This module is intended to implement integer/bitwise operations in OpenFHE's 
# BinFHE for demonstration purposes.  A more "real" version of this
# API would probably be written in C++ to leverage CPU parallelism and 
# consequently be much faster.
#
# It implements both secure and plaintext versions of these operations
# to simplify the writing of unit tests and similar.
#

import os
from typing import Callable, Iterable
from unittest import TestCase
import unittest
from xmlrpc.client import Boolean
import openfhe

class Encoder:
  """Base class for encoding and encrypting values."""

  def encode_bit(self, bit: bool) -> 'Wire':
    """Encode and encrypt a bit if applicable, returning a Wire"""
    raise NotImplementedError("encode_bit")

  def decode_bit(self, wire: 'Wire') -> bool:
    """Decrypt and decode a bit, returning a boolean"""
    raise NotImplementedError("decode_bit")

  def encode_int(self, i: int, sz: int) -> 'Circuit':
    """Encode and encrypt an integer, returning a Circuit representing
    the integer `i` with bit width `sz`   
    """
    bits = []
    s = i
    for _ in range(0, sz):
      bits.append(self.encode_bit(s & 1 == 1))
      s = s >> 1
    
    return Circuit(bits)

  def decode_int(self, c: 'Circuit') -> int:
    """Decrypt and decode a Circuit to an int"""
    v = 0
    for i in range(0, len(c.wires)):
      if self.decode_bit(c.wires[i]):
        v += 1 << i

    return v

class Wire:
  """Represents a single encrypted boolean value"""
  def __invert__(self) -> 'Wire':
    raise NotImplementedError("__invert__")

  def __and__(self, other: 'Wire') -> 'Wire':
    raise NotImplementedError("__and__")

  def __or__(self, other: 'Wire') -> 'Wire':
    raise NotImplementedError("__or__")

  def __xor__(self, other: 'Wire') -> 'Wire':
    raise NotImplementedError("__xor__")

  def adc(self, other: 'Wire') -> tuple['Wire', 'Wire']:
    """Add with carry with `other` returning a tuple of (sum of self and other, carry bit)"""
    return (self ^ other, self & other)

  def eq(self, other: 'Wire') -> 'Wire':
    """Is this wire equal to `other`"""
    return ~(self ^ other)
  
  def cond(self, then: 'Circuit', els: 'Circuit') -> 'Circuit':
    """If this Wire is 1, returns the result of the `then` 
    Circuit - otherwise returns the `els` Circuit"""
    assert(len(then.wires) == len(els.wires))
    lst: list[Wire] = list((self & thenwire) | (~self & elswire) for (thenwire,elswire) in zip(then.wires,els.wires))
    return Circuit(lst)
  
  def zero(self) -> 'Wire':
    """Return a zero wire of the same type as this wire"""
    return self & ~self
    
  def one(self) -> 'Wire':
    return self | ~self
  
  @staticmethod
  def any(ws: Iterable['Wire']) -> 'Wire':
    """Results in 1 if any of `ws` is 1 otherwise 0"""
    result = None
    for w in ws:
      if result is None:
        result = w
      else:
        result = w | result

    assert(result is not None)
    return result
  
  @staticmethod
  def all(ws: Iterable['Wire']) -> 'Wire':
    """Results in 1 if all of `ws` are 1 otherwise 0"""
    result = None
    for w in ws:
      if result is None:
        result = w
      else:
        result = w & result

    assert(result is not None)
    return result
  
# --- pt version ----------------------------------------------------------

class PlainEncoder(Encoder):
  """Plaintext version of the `Encoder` class - does not do encoding or encrypting,
  but is useful for unit testing
  """
  def encode_bit(self, bit: bool) -> Wire:
    return PlainWire(bit)

  def decode_bit(self, wire: Wire) -> bool:
    assert isinstance(wire, PlainWire)
    return wire.wire

class PlainWire(Wire):
  """Plaintext version of the `Encoder` class - does not do encoding or encrypting,
  but is useful for unit testing
  """
  def __init__(self, b: bool):
    self.wire = b

  def __invert__(self) -> 'PlainWire':
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
  """BinFHE backed version of `Encoder`"""
  def __init__(self, cc: openfhe.BinFHEContext, sk: openfhe.PrivateKey):
    self.cc = cc
    self.sk = sk

  def encode_bit(self, bit: bool) -> Wire:
      return BinFHEWire(self.cc, self.cc.Encrypt(self.sk, int(bit)))

  def decode_bit(self, wire: Wire) -> bool:
    assert isinstance(wire, BinFHEWire)
    return self.cc.Decrypt(self.sk, wire.wire) != 0

class BinFHEWire(Wire):
  """BinFHE version of `Wire`"""
  zerowire: 'BinFHEWire|None' = None
  onewire: 'BinFHEWire|None' = None

  def __init__(self, cc: openfhe.BinFHEContext, l: openfhe.LWECiphertext):
    self.cc = cc
    self.wire = l

  def __invert__(self) -> 'BinFHEWire':
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
      return ~self

    return BinFHEWire(self.cc, self.cc.EvalBinGate(openfhe.XOR, self.wire, other.wire))
  

# -- circuits -----------------------------------------------------------------

class Circuit:
  """A Circuit is a group of Wires along with operations that
  deal with these Wires as a group such as integer addition.

  The integer operations assume that the least significant bit appears 
  first in the list and for the time being operate on every integer as if
  it is unsigned.  In other words, `wires[x]` refers to the bit corresponding
  to the value of `2 ** x`
  """
  def __init__(self, wires: list[Wire]):
    """Create a Circuit with a list of Wires"""
    assert(len(wires) > 0)
    self.wires = wires
    self.onewire = None
    self.zerowire = None

  def derive_circuit(self, wires: list[Wire]) -> 'Circuit':
    """Effectively the same as __init__ but also copy a reference to 
    any cached one or zero wires"""
    assert(len(wires) > 0)
    circuit = Circuit(wires)
    circuit.zerowire = self.zerowire
    circuit.onewire = self.onewire
    return circuit

  def zero(self) -> Wire:
    """Get or create a zero valued Wire"""
    if self.zerowire is None:
      self.zerowire = self.wires[0] & ~self.wires[0]
    
    return self.zerowire
  
  def one(self) -> Wire:
    """Get or create a Wire with a value of one"""
    if self.onewire is None:
      self.onewire = self.wires[0] | ~self.wires[0]
    
    return self.onewire

  def lt(self, other: 'Circuit') -> Wire:
    """Returns a Wire of value 1 is `self` is less than `other`, 0 otherwise"""
    assert len(self.wires) == len(other.wires)
    is_lt = None
    for (w_i, o_i) in zip(self.wires, other.wires):
      bit_lt = (~w_i & o_i)
      if is_lt is None:
        is_lt = bit_lt
      else:
        is_lt = bit_lt | (w_i.eq(o_i) & is_lt)

    assert(is_lt is not None)
    return is_lt
  
  def eq(self, other: 'Circuit') -> Wire:
    """Return a Wire of value 1 if `self` is equal to `other`, 0 otherwise"""
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
    """Add two Circuits - any overflow wraps around"""
    assert len(self.wires) == len(other.wires)
    wires = []
    carry_in = self.zero()
    for i in range(0, len(self.wires)):
      (b, carry_out) = self.wires[i].adc(other.wires[i])
      wires.append(b | carry_in)
      carry_in = carry_out

    return self.derive_circuit(wires)
  
  def __rshift__(self, shift: int) -> 'Circuit':
    """Perform an unsigned right shift"""
    wires = []
    z = self.zero()
    for i in range(0, len(self.wires)):
      val = self.wires[i + shift] if i + shift < len(self.wires) else z
      wires.append(val)

    return Circuit(wires)
  
  def __lshift__(self, shift: int) -> 'Circuit':
    """Perform an unsigned left shift"""
    wires = []
    z = self.zero()
    for i in range(0, len(self.wires)):
      val = self.wires[i - shift] if i - shift >= 0 else z
      wires.append(val)

    return self.derive_circuit(wires)
  
  def __mul__(self, other: 'Circuit') -> 'Circuit':
    """Multiply two Circuits - any overflow wraps around"""
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
  
  def __and__(self, other: 'Circuit') -> 'Circuit':
    """Bitwise AND of two circuits - resulting circuit is equal in size to the smaller of the two"""
    result = []
    for (x, y) in zip(self.wires, other.wires):
      result.append(x & y)

    return self.derive_circuit(result)
  
  def __or__(self, other: 'Circuit') -> 'Circuit':
    """Bitwise OR of two circuits - resulting circuit is equal in size to the smaller of the two"""
    result = []
    for (x, y) in zip(self.wires, other.wires):
      result.append(x | y)

    return self.derive_circuit(result)
  
  def __invert__(self) -> 'Circuit':
    return self.derive_circuit(list(~w for w in self.wires))    

  def plain(self, val: int, sz: int | None = None) -> 'Circuit':
    """Make a circuit of the same size with all zeroes - any overflow is discarded"""
    if sz is None:
      sz = len(self.wires)

    assert sz > 0
    new_wires = []
    for i in range(sz):
      if val & 1:
        new_wires.append(self.one())
      else:
        new_wires.append(self.zero())

      val = val >> 1

    return self.derive_circuit(new_wires)

        



# -- unit testing -------------------------------------------------------------

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
      self.assertEqual(not b1.wire, enc.decode_bit(~b1))

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

  def cond_program(self, enc: Encoder):
    v5 = enc.encode_int(5, 8)
    v10 = enc.encode_int(10, 8)
    t = enc.encode_bit(True)
    f = enc.encode_bit(False)

    self.assertEqual(5, enc.decode_int(t.cond(v5, v10)))
    self.assertEqual(10, enc.decode_int(f.cond(v5, v10)))

  def plain_program(self, enc: Encoder):
    v5 = enc.encode_int(5, 8)
    v10 = v5.plain(10, 16)
    self.assertEqual(10, enc.decode_int(v10))

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

  def test_plain(self):
    self.run_program(self.plain_program)

  def test_cond(self):
    self.run_program(self.cond_program)

if __name__ == '__main__':
    unittest.main()
