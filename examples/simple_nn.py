import time
import openfhe as ofhe

import random

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime

from typing import Self


def nn_activation(cc: ofhe.CryptoContext, input: ofhe.Ciphertext):
    return cc.EvalMult(input, input)

class Neuron:
    def __init__(
        self, 
        cc: ofhe.CryptoContext,
        weights: list[ofhe.Ciphertext], 
        bias = None,
    ) -> Self:
        self.num_inputs = len(weights)
        self.weights = weights
        self.bias = cc.MakeCKKSPackedPlaintext([0.0])

    def set_id(self, neuron_id: int):
        self.neuron_id = neuron_id

    def set_bias(self, bias: ofhe.Ciphertext):
        self.bias = bias

    def neuron_from_plaintext(cc: ofhe.CryptoContext, weights: list[int]) -> Self:
        weights_ckks = []
        for w in weights:
            weights_ckks.append(cc.MakeCKKSPackedPlaintext([w]))
        return Neuron(cc, weights_ckks)

    def train(
        self,
        cc: ofhe.CryptoContext,
        inputs: list[ofhe.Ciphertext]
    ) -> ofhe.Ciphertext:
        if len(inputs) != self.num_inputs:
            raise ValueError(f"The number of inputs {len(inputs)} does not match the number of neuron inputs {self.num_inputs}")

        mults = map(lambda x, y: cc.EvalMult(x,y), inputs, self.weights)
        sum = reduce(lambda x, y: cc.EvalAdd(x,y), mults)
        sum = cc.EvalAdd(sum, self.bias)
        return nn_activation(cc, sum)

class NN:
    def __init__(
        self,
        cc: ofhe.CryptoContext,
        weights: list[list[ofhe.Ciphertext]],
        biases: list[ofhe.Ciphertext],
    ) -> Self:
        self.num_layers = len(weights)
        self.num_hidden_layers = len(weights[0])
        self.num_inputs = len(weights[0][0])

        self.weights = weights
        self.biases = biases

    def hidden_layer(
        self,
        cc: ofhe.CryptoContext,
        x: list[ofhe.Ciphertext],
        layer_num: int,
        hidden_layer_num: int,
    ):
        l = len(x)
        sum = cc.MakeCKKSPackedPlaintext([0])
        for i in range(l):
            weighted = cc.EvalMult(x[i], self.weights[layer_num][hidden_layer_num][i])
            weighted_bias = cc.EvalAdd(
                weighted, self.biases[layer_num][hidden_layer_num]
            )
            sum = cc.EvalAdd(weighted_bias, sum)
        return nn_activation(cc, sum)

    def neuron(
        self, cc: ofhe.CryptoContext, x: list[ofhe.Ciphertext], layer_num: int
    ) -> ofhe.Ciphertext:
        l = len(x)
        assert l == self.num_inputs

        layer_out = []
        for i in range(self.num_hidden_layers):
            out = self.hidden_layer(cc, x, layer_num, i)
            layer_out.append(out)
        return layer_out

    def forward(self, cc: ofhe.CryptoContext, x: list[ofhe.Ciphertext]):
        # Simplification
        assert len(x) == self.num_hidden_layers
        input = x
        for layer in range(self.num_layers):
            layer_out = self.neuron(cc, input, layer)
            input = layer_out
        return input


def rand_nn(
    cc: ofhe.CryptoContext, num_layers: int, num_hidden_layers: int, num_inputs: int
) -> Self:
    weights = [
        [
            [cc.MakeCKKSPackedPlaintext([i]) for i in range(num_inputs)]
            for _ in range(num_hidden_layers)
        ]
        for _ in range(num_layers)
    ]
    biases = [
        [cc.MakeCKKSPackedPlaintext([0.0]) for _ in range(num_hidden_layers)]
        for _ in range(num_layers)
    ]
    return (weights, biases)


def make_w_b(
    cc: ofhe.CryptoContext, weights: list[list[list[float]]], biases: list[list[float]]
) -> Self:
    weights_plt = [
        [
            [cc.MakeCKKSPackedPlaintext([w]) for w in weights[i][j]]
            for j in range(len(weights[i]))
        ]
        for i in range(len(weights))
    ]
    biases_plt = [
        [cc.MakeCKKSPackedPlaintext([b]) for b in biases[i]] for i in range(len(biases))
    ]
    return (weights_plt, biases_plt)


def train(cc: ofhe.CryptoContext, x: list[ofhe.Ciphertext], num_layers):
    print("Running NN..")
    num_inputs = len(x)
    num_hidden_layers = num_inputs
    (weights, biases) = rand_nn(cc, num_layers, num_hidden_layers, num_inputs)
    # (weights, biases) = make_w_b(cc, weights, biases)
    nn = NN(cc, weights, biases)
    result = nn.forward(cc, x)
    return result


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
    num_layers = 2
    (cc, _) = setup_context()

    # do some additional setup for openfhe that is key dependent
    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)

    # encode and encrypt inputs labels
    xs = [[random.random()] for i in range(num_inputs)]
    xs_pt = [cc.MakeCKKSPackedPlaintext(x) for x in xs]
    for x in xs_pt:
        x.SetLength(1)
    xs_ct = [cc.Encrypt(key_pair.publicKey, x_pt) for x_pt in xs_pt]

    # time and run the program
    start_ns = time.time_ns()
    results = train(cc, xs_ct, num_layers)
    end_ns = time.time_ns()

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
    num_layers = 2
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]
    train(cc, xs_ct, num_layers)


if __name__ == "__main__":
    main()
