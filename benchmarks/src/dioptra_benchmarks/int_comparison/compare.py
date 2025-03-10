from typing import Callable
from unittest import TestCase
from benchmark.circuit import Circuit, Wire
import benchmark.circuit as circuit
import random

def any_cmp(cmp: Callable[[Circuit, Circuit], Wire],lst1: list[Circuit], lst2: list[Circuit]) -> Wire:
  result = None
  assert(len(lst1) > 0 and len(lst2) > 0)
  result = None
  encoder = circuit.PlainEncoder()
  for elt1 in lst1:
    for elt2 in lst2:
      if result is None:
        result = cmp(elt1,elt2)
      else:
        result = result | cmp(elt1,elt2) 
  assert(result != None)
  return result

def any_eq(lst1: list[Circuit], lst2: list[Circuit]) -> Wire:
  return any_cmp(Circuit.eq, lst1, lst2)
      
class Tests(TestCase):
  def any_eq_correct(self, l1: list[int], l2: list[int]):
    expected = any(e1 == e2 for e1 in l1 for e2 in l2)
    encoder = circuit.PlainEncoder()
    
    c1 = [encoder.encode_int(e1, 16) for e1 in l1]
    c2 = [encoder.encode_int(e2, 16) for e2 in l2]
    self.assertEqual(expected, encoder.decode_bit(any_eq(c1, c2)), f"input lists {l1} and {l2}")

  def test_eq(self):
    self.any_eq_correct([1], [1])
    self.any_eq_correct([1], [2])

    ns = range(0, 10)
    for i in range(0, 100):
      l1 = random.choices(ns, k=5)
      l2 = random.choices(ns, k=5)
      self.any_eq_correct(l1, l2)




