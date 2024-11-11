import math

from dioptra.estimate import dioptra_estimation
from dioptra.pke.analyzer import Analyzer


@dioptra_estimation()
def unsupported1(cc: Analyzer):
    ct1 = cc.ArbitraryCT()
    poly_degree = 50
    lower_bound = 0
    upper_bound = 10
    cc.EvalChebyshevFunction(math.sqrt, ct1, lower_bound, upper_bound, poly_degree)
