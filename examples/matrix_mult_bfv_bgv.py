import time
import openfhe as ofhe

import random

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime
from dioptra.analyzer.calibration import PKECalibrationData

from typing import Self


def matrix_mult(
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
            sum = cc.MakePackedPlaintext([0])
            for k in range(l):
                mul = cc.EvalMult(x[i][k], y[k][j])
                sum = cc.EvalAdd(mul, sum)
            result[i][j] = sum
    return result


# make a cryptocontext and return the context and the parameters used to create it
def bgv1() -> tuple[
    ofhe.CryptoContext,
    ofhe.CCParamsBGVRNS,
    ofhe.KeyPair,
    list[ofhe.PKESchemeFeature],
]:
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBGVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)

    crypto_context = ofhe.GenCryptoContext(parameters)
    # Enable features that you wish to use
    features = [
        ofhe.PKESchemeFeature.PKE,
        ofhe.PKESchemeFeature.KEYSWITCH,
        ofhe.PKESchemeFeature.LEVELEDSHE,
    ]
    for feature in features:
        crypto_context.Enable(feature)

    # Sample Program: Step 2: Key Generation

    # Generate a public/private key pair
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair, features)


# Actually run program and time it
def main():
    rows = 5
    cols = 5
    (cc, _, key_pair, _) = bgv1()

    # encode and encrypt inputs labels
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
    result_ct = matrix_mult(cc, x_ct, y_ct)
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
