from typing import Callable
from unittest import TestCase
from benchmark.circuit import Circuit, Wire
import benchmark.circuit as circuit
import random

# Determine if there is any common elements between `cs1` and `cs2`
def any_eq(cs1: list[Circuit], cs2: list[Circuit]) -> Wire:
  return Wire.any(c1.eq(c2) for c1 in cs1 for c2 in cs2)

# Determine if everything in `cs1` is pointwise less than everything in `cs2`
def zip_lt(cs1: list[Circuit], cs2: list[Circuit]) -> Wire:
  return Wire.all(c1.lt(c2) for (c1, c2) in zip(cs1, cs2))
      
class Tests(TestCase):
  def any_eq_correct(self, l1: list[int], l2: list[int]):
    expected = any(e1 == e2 for e1 in l1 for e2 in l2)
    encoder = circuit.PlainEncoder()
    
    c1 = [encoder.encode_int(e1, 16) for e1 in l1]
    c2 = [encoder.encode_int(e2, 16) for e2 in l2]
    self.assertEqual(expected, encoder.decode_bit(any_eq(c1, c2)), f"input lists {l1} and {l2}")

  def zip_lt_correct(self, l1: list[int], l2: list[int]):
    expected = all(e1 < e2 for (e1, e2) in zip(l1, l2))
    encoder = circuit.PlainEncoder()

    c1 = [encoder.encode_int(e1, 16) for e1 in l1]
    c2 = [encoder.encode_int(e2, 16) for e2 in l2]
    self.assertEqual(expected, encoder.decode_bit(zip_lt(c1, c2)), f"input lists {l1} and {l2}")

  def test_eq(self):
    self.any_eq_correct([1], [1])
    self.any_eq_correct([1], [2])

    ns = range(0, 10)
    for i in range(0, 100):
      l1 = random.choices(ns, k=5)
      l2 = random.choices(ns, k=5)
      self.any_eq_correct(l1, l2)

  def test_lt(self):
    self.zip_lt_correct([1], [1])
    self.zip_lt_correct([1], [2])
    self.zip_lt_correct([2], [1])

    ns = range(0, 10)
    for i in range(0, 100):
      l1 = random.choices(ns, k=5)
      l2 = random.choices(ns, k=5)
      self.zip_lt_correct(l1, l2)




