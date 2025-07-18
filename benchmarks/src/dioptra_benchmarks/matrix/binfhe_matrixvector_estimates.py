from benchmark.circuit import BinFHEWire, Circuit
from matrix import BinMath, CiphertextMatrix
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.estimate import dioptra_binfhe_estimation

def mk_arbitrary_circuit(cc: BinFHEAnalyzer) -> Circuit:
  return Circuit(list(BinFHEWire(cc, cc.ArbitraryCT()) for _ in range(8)))

def mk_arbitrary_matrix(cc: BinFHEAnalyzer, rows: int, cols: int):
  return CiphertextMatrix(list(list(mk_arbitrary_circuit(cc) for _ in range(cols)) for _ in range(rows)), BinMath())

@dioptra_binfhe_estimation(description="multiply 4x4 matrix by a 4x4 matrix")
def mul4x4matrix_by_vector(cc: BinFHEAnalyzer):
  _ = mk_arbitrary_matrix(cc, 4, 4) * mk_arbitrary_matrix(cc, 4, 4)

@dioptra_binfhe_estimation(description="multiply 8x8 matrix by an 8x8 matrix")
def mul8x8matrix_by_vector(cc: BinFHEAnalyzer):
  _ = mk_arbitrary_matrix(cc, 8, 8) * mk_arbitrary_matrix(cc, 8, 8)

@dioptra_binfhe_estimation(description="multiply 16x16 matrix by a 16x16 matrix")
def mul16x16matrix_by_vector(cc: BinFHEAnalyzer):
  _ = mk_arbitrary_matrix(cc, 16, 16) * mk_arbitrary_matrix(cc, 16, 16)

@dioptra_binfhe_estimation(description="multiply 64x64 matrix by a 64x64 matrix")
def mul64x64matrix_by_vector(cc: BinFHEAnalyzer):
  _ = mk_arbitrary_matrix(cc, 64, 64) * mk_arbitrary_matrix(cc, 64, 1)

# Running the analysis for 64x64 takes a long time, so this might take a REALLY long time

# @dioptra_binfhe_estimation(description="multiply 256x256 matrix by a vector")
# def mul256x256matrix_by_vector(cc: BinFHEAnalyzer):
#   _ = mk_arbitrary_matrix(cc, 256, 256) * mk_arbitrary_matrix(cc, 256, 1)