import time
import openfhe as ofhe
<<<<<<< HEAD
=======
from contexts import bfv1
>>>>>>> ae41317 (Fix bugs with BFV matrix mult)

import random

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime
from dioptra.analyzer.calibration import PKECalibrationData

from typing import Self

<<<<<<< HEAD

def matrix_mult(
=======
class Scheme: 
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        raise NotImplementedError("Plaintext packing is not implemented for this scheme")
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        raise NotImplementedError("The zero value is not implemented for this scheme")
    def bootstrap(self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        pass

class BFV(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
       return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return value

def matrix_mult(
    scheme: Scheme,
>>>>>>> ae41317 (Fix bugs with BFV matrix mult)
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
<<<<<<< HEAD
            sum = cc.MakePackedPlaintext([0])
            for k in range(l):
                mul = cc.EvalMult(x[i][k], y[k][j])
                sum = cc.EvalAdd(mul, sum)
=======
            sum = scheme.zero(cc)
            for k in range(l):
                mul = cc.EvalMult(x[i][k], y[k][j])
                sum = cc.EvalAdd(mul, sum)
                if k % 5 == 0:
                    sum = scheme.bootstrap(cc, sum)
>>>>>>> ae41317 (Fix bugs with BFV matrix mult)
            result[i][j] = sum
    return result


<<<<<<< HEAD
# make a cryptocontext and return the context and the parameters used to create it
def bfv1() -> tuple[
    ofhe.CryptoContext,
    ofhe.CCParamsBFVRNS,
    ofhe.KeyPair,
    list[ofhe.PKESchemeFeature],
]:
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBFVRNS()
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


=======
>>>>>>> ae41317 (Fix bugs with BFV matrix mult)
# Actually run program and time it
def main():
    rows = 5
    cols = 5
    (cc, _, key_pair, _) = bfv1()

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
<<<<<<< HEAD
    result_ct = matrix_mult(cc, x_ct, y_ct)
=======
    result_ct = matrix_mult(BFV(), cc, x_ct, y_ct)
>>>>>>> ae41317 (Fix bugs with BFV matrix mult)
    end_ns = time.time_ns()

    rows = len(xs)
    cols = len(ys[0])
    result = [[[random.random()] for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            result_dec = cc.Decrypt(key_pair.secretKey, result_ct[i][j])
            result_dec.SetLength(1)
<<<<<<< HEAD
            result[i][j] = result_dec.GetCKKSPackedValue()
=======
            result[i][j] = result_dec.GetPackedValue()
>>>>>>> ae41317 (Fix bugs with BFV matrix mult)
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
