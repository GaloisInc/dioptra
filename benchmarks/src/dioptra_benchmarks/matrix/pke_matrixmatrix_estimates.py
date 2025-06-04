from typing import Callable
from dioptra.estimate import EstimationCases, dioptra_custom_estimation
from matrix import *

def mk_arbitrary_matrix(cc: Analyzer, rows: int, cols: int):
  return CiphertextMatrix(list(list(cc.ArbitraryCT() for _ in range(cols)) for _ in range(rows)), PkeMath(cc))

def do_mul(dim1: tuple[int, int], dim2: tuple[int, int]) -> Callable:
  def mul(cc: Analyzer):
    (r1, c1) = dim1
    (r2, c2) = dim2
    _ = mk_arbitrary_matrix(cc, r1, c1) * mk_arbitrary_matrix(cc, r2, c2)

  return mul

@dioptra_custom_estimation()
def matrix_mul(ec: EstimationCases):
  dims = [4, 8, 16, 32, 64, 128]
  for x in dims:
    for y in [d for d in dims if d <= x]:
      desc = f"multiply {y}x{x} matrix by {x}x{y} matrix"
      ec.add_pke_case(do_mul((y,x), (x,y)), desc)