""" Matrix Multiplication in BGV

This example implements matrix multiplication for variable length
matrices in BGV.
"""
import time
import openfhe as ofhe
from contexts import bgv1
from schemes import Scheme

import random

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime
from dioptra.analyzer.calibration import PKECalibrationData

from typing import Self

class BGV(Scheme):
    """Class which defines BGV specific behavior"""
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        #OpenFHE does not support boostrapping for BGV
        return value

def matrix_mult(
    scheme: Scheme,
    cc: ofhe.CryptoContext,
    x: list[list[ofhe.Ciphertext]],
    y: list[list[ofhe.Ciphertext]],
):
    """ Matrix Multiplication in FHE"""
    
    assert len(x[0]) == len(y)
    print("Running Matrix Multiplication ..")

    rows = len(x)
    cols = len(y[0])
    l = len(x[0])

    result = [[0 for _ in range(rows)] for _ in range(cols)]
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
    rows = 5
    cols = 5
    # BGV specific setup
    (cc, _, key_pair, _) = bgv1()

    # encode and encrypt inputs labels, the inputs are generated at random
    xs = [[[random.randint(0, 10)] for _ in range(cols)] for _ in range(rows)]
    ys = [[[random.randint(0, 10)] for _ in range(cols)] for _ in range(rows)]

    x_ct = [[[None] for _ in range(len(xs[0]))] for _ in range(len(xs))]
    for i in range(len(xs)):
        for j in range(len(xs[0])):
            x_pt = cc.MakePackedPlaintext(xs[i][j])
            x_pt.SetLength(1)
            x_enc = cc.Encrypt(key_pair.publicKey, x_pt)
            x_ct[i][j] = x_enc

    y_ct = [[[None] for _ in range(len(ys[0]))] for _ in range(len(ys))]
    for i in range(len(ys)):
        for j in range(len(ys[0])):
            y_pt = cc.MakePackedPlaintext(ys[i][j])
            y_pt.SetLength(1)
            y_enc = cc.Encrypt(key_pair.publicKey, y_pt)
            y_ct[i][j] = y_enc

    # time and run the program
    start_ns = time.time_ns()
    result_ct = matrix_mult(BGV(), cc, x_ct, y_ct)
    end_ns = time.time_ns()

    # decrypt results
    rows = len(xs)
    cols = len(ys[0])
    result = [[[random.random()] for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
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
