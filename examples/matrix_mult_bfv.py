"""Matrix Multiplication in BFV

This example implements matrix multiplication for variable length
matrices in BFV. This example supports multiplying matrices of 
different dimensions.
"""

import time
import openfhe as ofhe
from contexts import bfv1
from schemes import Scheme

import random

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime
from dioptra.analyzer.calibration import PKECalibrationData

from typing import Self


class BFV(Scheme):
    """Class which defines BFV specific behavior"""

    def make_plaintext(
        self, cc: ofhe.CryptoContext, value: list[int]
    ) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)

    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])

    def bootstrap(
        self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext
    ) -> ofhe.Ciphertext:
        return value


def matrix_mult(
    scheme: Scheme,
    cc: ofhe.CryptoContext,
    x: list[list[ofhe.Ciphertext]],
    y: list[list[ofhe.Ciphertext]],
):
    """Matrix Multiplication in FHE"""

    assert len(x[0]) == len(y)
    print("Running Matrix Multiplication ..")

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


# Actually run program and time it
def main():
    xrows = 3
    xcols = 3

    yrows = xcols
    ycols = 1
    (cc, _, key_pair, _) = bfv1()

    # encode and encrypt inputs labels, the inputs are generated at random
    xs = [[[random.randint(0, 10)] for _ in range(xcols)] for _ in range(xrows)]
    ys = [[[random.randint(0, 10)] for _ in range(ycols)] for _ in range(yrows)]

    x_ct = [[[None] for _ in range(xcols)] for _ in range(xrows)]
    for i in range(xrows):
        for j in range(xcols):
            x_pt = cc.MakePackedPlaintext(xs[i][j])
            x_pt.SetLength(1)
            x_enc = cc.Encrypt(key_pair.publicKey, x_pt)
            x_ct[i][j] = x_enc

    y_ct = [[[None] for _ in range(ycols)] for _ in range(yrows)]
    for i in range(yrows):
        for j in range(ycols):
            y_pt = cc.MakePackedPlaintext(ys[i][j])
            y_pt.SetLength(1)
            y_enc = cc.Encrypt(key_pair.publicKey, y_pt)
            y_ct[i][j] = y_enc

    # time and run the program
    start_ns = time.time_ns()
    result_ct = matrix_mult(BFV(), cc, x_ct, y_ct)
    end_ns = time.time_ns()

    # decrypt results
    result = [[[random.random()] for _ in range(ycols)] for _ in range(xrows)]
    for i in range(xrows):
        for j in range(ycols):
            result_dec = cc.Decrypt(key_pair.secretKey, result_ct[i][j])
            result_dec.SetLength(1)
            result[i][j] = result_dec.GetPackedValue()
        print(result[i])

    print(f"Actual runtime: {format_ns(end_ns - start_ns)}")


@dioptra_runtime()
def report_runtime(cc: Analyzer):
    rows = 5
    cols = 5
    x_ct = [[cc.ArbitraryCT() for _ in range(cols)] for _ in range(rows)]
    y_ct = [[cc.ArbitraryCT() for _ in range(cols)] for _ in range(rows)]
    matrix_mult(cc, x_ct, y_ct)


if __name__ == "__main__":
    main()
