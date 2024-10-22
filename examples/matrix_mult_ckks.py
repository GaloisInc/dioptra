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
    rows = 2
    cols = 2
    (cc, _, key_pair, _) = ckks_small1()

    # encode and encrypt inputs labels
    xs = [[[random.random()] for _ in range(cols)] for _ in range(rows)]
    ys = [[[random.random()] for _ in range(cols)] for _ in range(rows)]

    x_ct = [[[random.random()] for _ in range(len(xs[0]))] for _ in range(len(xs))]
    for i in range(len(xs)):
        for j in range(len(xs[0])):
            x_pt = cc.MakeCKKSPackedPlaintext(xs[i][j])
            x_pt.SetLength(1)
            x_enc = cc.Encrypt(key_pair.publicKey, x_pt)
            x_ct[i][j] = x_enc

    y_ct = [[[random.random()] for _ in range(len(ys[0]))] for _ in range(len(ys))]
    for i in range(len(ys)):
        for j in range(len(ys[0])):
            y_pt = cc.MakeCKKSPackedPlaintext(ys[i][j])
            y_pt.SetLength(1)
            y_enc = cc.Encrypt(key_pair.publicKey, y_pt)
            y_ct[i][j] = y_enc

    # time and run the program
    start_ns = time.time_ns()
    result_ct = matrix_mult(CKKS(), cc, x_ct, y_ct)
    end_ns = time.time_ns()

    rows = len(xs)
    cols = len(ys[0])
    result = [[[random.random()] for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
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
