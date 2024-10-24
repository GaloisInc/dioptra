import math
from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.decorator import dioptra_runtime


@dioptra_runtime()
def unsupported1(cc: Analyzer):
  ct1 = cc.ArbitraryCT()
  poly_degree = 50
  lower_bound = 0
  upper_bound = 10
  result = cc.EvalChebyshevFunction(math.sqrt,ct1, lower_bound, upper_bound, poly_degree)
