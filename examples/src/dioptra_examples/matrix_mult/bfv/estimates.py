from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.decorator import dioptra_runtime

from dioptra_examples.matrix_mult import matrix_mult
from dioptra_examples.schemes import BFV


@dioptra_runtime()
def matrix_vec_3x1_to_3x1(cc: Analyzer):
    xrows = 3
    xcols = 3

    yrows = xcols
    ycols = 1

    x_ct = [[cc.ArbitraryCT() for _ in range(xcols)] for _ in range(xrows)]
    y_ct = [[cc.ArbitraryCT() for _ in range(ycols)] for _ in range(yrows)]
    matrix_mult(BFV(), cc, x_ct, y_ct)
