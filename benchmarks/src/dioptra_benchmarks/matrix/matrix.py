import sys
from typing import Iterable
import benchmark.contexts as contexts
import benchmark.common as common
import random
import openfhe as ofhe
import argparse
import re

from dioptra.context import dioptra_binfhe_context, dioptra_pke_context
from dioptra.estimate import dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer
from benchmark.circuit import BinFHEEncoder, Circuit

class CiphertextMath[EncryptedType]:
  def mul_elt(self, e1: EncryptedType, e2: EncryptedType) -> EncryptedType:
    raise NotImplementedError("mul_elt not implemented")
  
  def add_elt(self, e1: EncryptedType, e2: EncryptedType) -> EncryptedType:
    raise NotImplementedError("add_elt not implemented")

class MatrixBuilder[EncryptedType, KeyType]:
  def get_math(self) -> CiphertextMath[EncryptedType]:
    raise NotImplementedError("get_math not implemented")

  def random(self, key: KeyType) -> EncryptedType:
    raise NotImplementedError("random not implemented")
  
  def random_matrix(self, rows: int, cols: int, key: KeyType) -> 'CiphertextMatrix[EncryptedType]':
    return CiphertextMatrix(list(list(self.random(key) for _ in range(cols)) for _ in range(rows)), self.get_math())

class CiphertextMatrix[ElementType]:
  def __init__(self, rows: list[list[ElementType]], math: CiphertextMath[ElementType]):
    if len(rows) == 0:
      raise ValueError("cannot create matrix from empty list of rows")

    if not all(len(row) == len(rows[0]) for row in rows):
      raise ValueError("matrix rows are not all of the same length!")

    self.math = math
    self.rows = rows
    
  def dim(self) -> tuple[int, int]:
    return (len(self.rows), len(self.rows[0]))
  
  def row(self, n: int) -> Iterable[ElementType]:
    return self.rows[n]
  
  def col(self, n: int) -> Iterable[ElementType]:
    return [row[n] for row in self.rows]
  
  def __mul__(self, other: 'CiphertextMatrix') -> 'CiphertextMatrix':
    (r1, c1) = self.dim()
    (r2, c2) = other.dim()
    if c1 != r2:
      raise ValueError(f"cannot multiply a {r1}x{c1} matrix by a {r2}x{c2} matrix - number of columns in the first matrix must be equal to number of rows in the second")
    
    rows = []
    for row_idx in range(r1):
      row = []
      for col_idx in range(c2):
        row.append(self.dotprod(self.row(row_idx), other.col(col_idx)))

      rows.append(row)

    return  CiphertextMatrix(rows, self.math)
  
  def dotprod(self, x: Iterable[ElementType], y: Iterable[ElementType]) -> ElementType:
    """dot product of two nonempty iterables of equivalent length"""
    x_iter = iter(x)
    y_iter = iter(y)
    result = None

    while True:
      x_val = next(x_iter, None)
      y_val = next(y_iter, None)

      if x_val is None and y_val is None:
        assert result != None
        return result
      
      if x_val is None or y_val is None:
        raise ValueError("dot product not valid for inputs of different length")
      
      xy_val = self.math.mul_elt(x_val, y_val)
      if result is None:
        result = xy_val
      else:
        result = self.math.add_elt(result, xy_val)

class PkeMath(CiphertextMath[ofhe.Ciphertext]):
  def __init__(self, cc: ofhe.CryptoContext):
    self.cc = cc

  def mul_elt(self, e1: ofhe.Ciphertext, e2: ofhe.Ciphertext) -> ofhe.Ciphertext:
    return self.cc.EvalMult(e1, e2)
  
  def add_elt(self, e1: ofhe.Ciphertext, e2: ofhe.Ciphertext) -> ofhe.Ciphertext:
    return self.cc.EvalAdd(e1, e2)

class PkeFloatBuilder(MatrixBuilder[ofhe.Ciphertext, ofhe.PublicKey]):
  def __init__(self, cc: ofhe.CryptoContext):
    self.cc = cc

  def get_math(self) -> CiphertextMath:
    return PkeMath(self.cc)
  
  def random(self, pkey: ofhe.PublicKey) -> ofhe.Ciphertext:
    ptxt = self.cc.MakeCKKSPackedPlaintext([random.random()])
    return self.cc.Encrypt(pkey, ptxt)

class PkeIntegerBuilder(CiphertextMath[ofhe.Ciphertext], MatrixBuilder[ofhe.Ciphertext, ofhe.PublicKey]):
  def __init__(self, cc: ofhe.CryptoContext):
    self.cc = cc

  def get_math(self):
    return PkeMath(self.cc)
  
  def random(self, pkey: ofhe.PublicKey) -> ofhe.Ciphertext:
    ptxt = self.cc.MakePackedPlaintext([random.randrange(0, 256)])
    return self.cc.Encrypt(pkey, ptxt)

class BinMath(CiphertextMath[Circuit]):
  def mul_elt(self, e1: Circuit, e2: Circuit) -> Circuit:
    return e1 * e2
  
  def add_elt(self, e1: Circuit, e2: Circuit) -> Circuit:
    return e1 + e2
  
class BinBuilder(MatrixBuilder[Circuit, ofhe.LWEPrivateKey]):
  def __init__(self, cc: ofhe.BinFHEContext):
    self.cc = cc

  def get_math(self):
    return BinMath()
  
  def random(self, sk: ofhe.LWEPrivateKey) -> Circuit:
    encoder = BinFHEEncoder(self.cc, sk)
    ptxt = random.randrange(0, 256)
    return encoder.encode_int(ptxt, sk)

  