from dioptra.estimate import dioptra_pke_estimation
from matrix import *

def mk_arbitrary_matrix(cc: Analyzer, rows: int, cols: int):
  return CiphertextMatrix(list(list(cc.ArbitraryCT() for _ in range(cols)) for _ in range(rows)), PkeMath(cc))

@dioptra_pke_estimation(description="multiply 4x4 matrix by a vector")
def mul4x4matrix_by_vector(cc: Analyzer):
  _ = mk_arbitrary_matrix(cc, 4, 4) * mk_arbitrary_matrix(cc, 4, 1)

@dioptra_pke_estimation(description="multiply 8x8 matrix by a vector")
def mul8x8matrix_by_vector(cc: Analyzer):
  _ = mk_arbitrary_matrix(cc, 8, 8) * mk_arbitrary_matrix(cc, 8, 1)

@dioptra_pke_estimation(description="multiply 16x16 matrix by a vector")
def mul16x16matrix_by_vector(cc: Analyzer):
  _ = mk_arbitrary_matrix(cc, 16, 16) * mk_arbitrary_matrix(cc, 16, 1)

@dioptra_pke_estimation(description="multiply 64x64 matrix by a vector")
def mul64x64matrix_by_vector(cc: Analyzer):
  _ = mk_arbitrary_matrix(cc, 64, 64) * mk_arbitrary_matrix(cc, 64, 1)

@dioptra_pke_estimation(description="multiply 256x256 matrix by a vector")
def mul256x256matrix_by_vector(cc: Analyzer):
  _ = mk_arbitrary_matrix(cc, 256, 256) * mk_arbitrary_matrix(cc, 256, 1)