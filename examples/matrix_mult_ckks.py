import time
import openfhe as ofhe

import random

from dioptra.analyzer.metrics.analysisbase import Analyzer
from dioptra.analyzer.metrics.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime
from dioptra.analyzer.calibration import PKECalibrationData

from typing import Self

def matrix_mult(cc: ofhe.CryptoContext, x: list[list[ofhe.Ciphertext]],  y: list[list[ofhe.Ciphertext]]):
    assert len(x[0]) == len(y) 
    print("Running Matrix Multiplication ..")

    rows = len(x)
    cols = len(y[0])
    l = len(x[0])

    result = [[0 for _ in range(rows)] for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            sum = cc.MakeCKKSPackedPlaintext([0])
            for k in range(l):
                mul = cc.EvalMult(x[i][k], y[k][j])
                sum = cc.EvalAdd(mul, sum)
            result[i][j] = sum
    return result

# make a cryptocontext and return the context and the parameters used to create it
def setup_context() -> tuple[ofhe.CryptoContext, ofhe.CCParamsCKKSRNS]:
    print("Setting up FHE program..")
    parameters = ofhe.CCParamsCKKSRNS()

    secret_key_dist = ofhe.SecretKeyDist.UNIFORM_TERNARY
    parameters.SetSecretKeyDist(secret_key_dist)

    parameters.SetSecurityLevel(ofhe.SecurityLevel.HEStd_128_classic)
    parameters.SetRingDim(1<<17)

    if ofhe.get_native_int()==128:
        rescale_tech = ofhe.ScalingTechnique.FIXEDAUTO
        dcrt_bits = 78
        first_mod = 89
    else:
        rescale_tech = ofhe.ScalingTechnique.FLEXIBLEAUTO
        dcrt_bits = 59
        first_mod = 60
    
    parameters.SetScalingModSize(dcrt_bits)
    parameters.SetScalingTechnique(rescale_tech)
    parameters.SetFirstModSize(first_mod)

    level_budget = [4, 4]

    levels_available_after_bootstrap = 10

    depth = levels_available_after_bootstrap + ofhe.FHECKKSRNS.GetBootstrapDepth(level_budget, secret_key_dist)

    parameters.SetMultiplicativeDepth(depth)

    cryptocontext = ofhe.GenCryptoContext(parameters)
    cryptocontext.Enable(ofhe.PKESchemeFeature.PKE)
    cryptocontext.Enable(ofhe.PKESchemeFeature.KEYSWITCH)
    cryptocontext.Enable(ofhe.PKESchemeFeature.LEVELEDSHE)
    cryptocontext.Enable(ofhe.PKESchemeFeature.ADVANCEDSHE)
    cryptocontext.Enable(ofhe.PKESchemeFeature.FHE)

    cryptocontext.EvalBootstrapSetup(level_budget)
    print("Setup complete..")
    return (cryptocontext, parameters)

# Actually run program and time it
def main():
    rows = 5
    cols = 5 
    (cc, _) = setup_context()

    # do some additional setup for openfhe that is key dependent
    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)

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


if __name__ == '__main__':
    main()