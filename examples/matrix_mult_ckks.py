""" Matrix Multiplication in CKKS

This example implements matrix multiplication for variable length
matrices in CKKS. This example bootstraps after a set number of 
multiplications and handles large matrices. This example supports 
multiplying matrices of different dimensions.
"""
import time
import openfhe as ofhe
from contexts import ckks1, ckks_small1
from schemes import Scheme

import random

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime
from dioptra.analyzer.calibration import PKECalibrationData

from typing import Self

class CKKS(Scheme):
    """Class which defines CKKS specific behavior"""
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext([0.0])
    def bootstrap(self, cc: ofhe.CryptoContext,  value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return cc.EvalBootstrap(value)     

def matrix_mult(
    scheme: Scheme,
    cc: ofhe.CryptoContext,
    x: list[list[ofhe.Ciphertext]],
    y: list[list[ofhe.Ciphertext]],
):
    """ Matrix Multiplication in FHE

    The aggregated result is bootstrapped every 5th multiplication.
    """
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
    # CKKS specific setup
    (cc, _, key_pair, _) = ckks1()

    # encode and encrypt inputs labels, the inputs are generated at random
    xs = [[[random.random()] for _ in range(xcols)] for _ in range(xrows)]
    ys = [[[random.random()] for _ in range(ycols)] for _ in range(yrows)]

    x_ct = [[[None] for _ in range(xcols)] for _ in range(xrows)]
    for i in range(xrows):
        for j in range(xcols):
            x_pt = cc.MakeCKKSPackedPlaintext(xs[i][j])
            x_pt.SetLength(1)
            x_enc = cc.Encrypt(key_pair.publicKey, x_pt)
            x_ct[i][j] = x_enc

    y_ct = [[[0] for _ in range(ycols)] for _ in range(yrows)]
    for i in range(yrows):
        for j in range(ycols):
            y_pt = cc.MakeCKKSPackedPlaintext(ys[i][j])
            y_pt.SetLength(1)
            y_enc = cc.Encrypt(key_pair.publicKey, y_pt)
            y_ct[i][j] = y_enc

    # time and run the program
    start_ns = time.time_ns()
    result_ct = matrix_mult(CKKS(), cc, x_ct, y_ct)
    end_ns = time.time_ns()

    # decrypt results
    result = [[[random.random()] for _ in range(ycols)] for _ in range(xrows)]
    for i in range(xrows):
        for j in range(ycols):
            result_dec = cc.Decrypt(key_pair.secretKey, result_ct[i][j])
            result_dec.SetLength(1)
            result[i][j] = result_dec.GetCKKSPackedValue()
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
