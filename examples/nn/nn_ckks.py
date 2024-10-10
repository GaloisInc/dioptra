import openfhe as ofhe

from schemes import CKKS
from nn import NN
from time import time_ns
from random import random
from functools import reduce
from typing import Self

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime

# make a cryptocontext and return the context and the parameters used to create it
def setup_context() -> tuple[ofhe.CryptoContext, ofhe.CCParamsCKKSRNS]:
    print("Setting up FHE program..")
    parameters = ofhe.CCParamsCKKSRNS()

    secret_key_dist = ofhe.SecretKeyDist.UNIFORM_TERNARY
    parameters.SetSecretKeyDist(secret_key_dist)

    parameters.SetSecurityLevel(ofhe.SecurityLevel.HEStd_128_classic)
    parameters.SetRingDim(1 << 17)

    if ofhe.get_native_int() == 128:
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

    depth = levels_available_after_bootstrap + ofhe.FHECKKSRNS.GetBootstrapDepth(
        level_budget, secret_key_dist
    )

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
    num_inputs = 2
    (cc, parameters) = setup_context()

    # do some additional setup for openfhe that is key dependent
    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)
    cc.EvalBootstrapKeyGen(key_pair.secretKey, parameters.GetRingDim() >> 1)

    # encode and encrypt inputs labels
    xs = [[random()] for i in range(num_inputs)]
    xs_pt = [cc.MakeCKKSPackedPlaintext(x) for x in xs]
    for x in xs_pt:
        x.SetLength(1)
    xs_ct = [cc.Encrypt(key_pair.publicKey, x_pt) for x_pt in xs_pt]

    # Generate arbitrary nn 
    neuron_weights = [0.1 for _ in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights, layer_weights]
    nn = NN.nn_from_plaintexts(cc, CKKS(), nn_weights)

    # time and run the program
    start_ns = time_ns()
    results = nn.train(cc, xs_ct)
    end_ns = time_ns()

    results_unpacked = []
    for r in results:
        result = cc.Decrypt(key_pair.secretKey, r)
        result.SetLength(1)
        results_unpacked.append(result.GetCKKSPackedValue())
    print(results_unpacked)

    print(f"Actual runtime: {format_ns(end_ns - start_ns)}")


@dioptra_runtime()
def report_runtime(cc: Analyzer):
    num_inputs = 2
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]

    # Generate arbitrary nn 
    neuron_weights = [0.1 for _ in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights, layer_weights]
    nn = NN.nn_from_plaintexts(cc, CKKS(), nn_weights)

    nn.train(cc, xs_ct)


if __name__ == "__main__":
    main()