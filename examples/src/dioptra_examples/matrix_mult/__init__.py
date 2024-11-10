"""Matrix Multiplication

This example implements matrix multiplication for variable length
matrices. This example supports multiplying matrices of 
different dimensions.
"""

import openfhe as ofhe

from dioptra_examples.schemes import Scheme


def matrix_mult(
    scheme: Scheme,
    cc: ofhe.CryptoContext,
    x: list[list[ofhe.Ciphertext]],
    y: list[list[ofhe.Ciphertext]],
):
    """Matrix Multiplication in FHE"""

    assert len(x[0]) == len(y)

    rows = len(x)
    cols = len(y[0])
    l = len(x[0])

    result = [[None for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            sum = scheme.zero(cc)
            for k in range(l):
                mul = cc.EvalMult(x[i][k], y[k][j])
                sum = cc.EvalAdd(mul, sum)
                if k % 5 == 0:
                    sum = scheme.bootstrap(cc, sum)
            result[i][j] = sum
    return result
