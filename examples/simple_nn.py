import openfhe as ofhe

from time import time_ns
from random import random
from functools import reduce
from typing import Self

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime

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

class Layer:
    def __init__(
        self, 
        cc: ofhe.CryptoContext,
        neurons: list[Neuron],
        bias = None,
    ) -> Self:
        self.num_neuron = len(neurons)

        for i, neuron in enumerate(neurons):
            neuron.set_id(i)   
            if bias != None:
                neuron.set_bias(bias)      
        self.neurons = neurons

    def set_id(self, layer_id: int):
        self.layer_id = layer_id

    def layer_from_plaintexts(cc: ofhe.CryptoContext, weights_layer: list[list[int]]) -> Self:
        neurons = []
        for weights_neuron in weights_layer:
            neuron = Neuron.neuron_from_plaintext(cc, weights_neuron)
            neurons.append(neuron)
        return Layer(cc, neurons)

    def train(
        self, 
        cc: ofhe.CryptoContext, 
        inputs: list[ofhe.Ciphertext]
        ) -> list[ofhe.Ciphertext]:
        self.check_correctness(len(inputs))

        layer_out = []
        for neuron in self.neurons:
            neuron_out = neuron.train(cc, inputs)
            layer_out.append(neuron_out)
        return layer_out

    def check_correctness(self, num_inputs: int):
        for neuron in self.neurons:
            assert num_inputs == neuron.num_inputs, f"On Layer #{self.layer_id}: Number of inputs{num_inputs} != Indegree of Neuron #{neuron.neuron_id} is {neuron.num_inputs}" 


class NN:
    def __init__(
        self,
        cc: ofhe.CryptoContext,
        layers: list[Layer] 
    ) -> Self:
        self.num_layers = len(layers)
        for i, layer in enumerate(layers):
            layer.set_id(i)
        self.layers = layers

    def nn_from_plaintexts(cc: ofhe.CryptoContext, weights_nn: list[list[list[float]]]) -> Self:
        layers = []
        for weights_layer in weights_nn:
            layer = Layer.layer_from_plaintexts(cc, weights_layer)
            layers.append(layer)
        return NN(cc, layers)

    def train(
        self,
        cc: ofhe.CryptoContext,
        inputs: list[ofhe.Ciphertext]
    ) -> ofhe.Ciphertext:
        layer_input = inputs
        for layer in self.layers:
            layer_input = layer.train(cc, layer_input)
        return layer_input


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

    # Generate arbitrary nn 
    neuron_weights = [0.1, 0.4]
    layer_weights = [neuron_weights, neuron_weights]
    nn_weights = [layer_weights, layer_weights]
    nn = NN.nn_from_plaintexts(cc, nn_weights)

    # time and run the program
    start_ns = time_ns()
    results = train(cc, xs_ct, num_layers)
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
    num_layers = 2
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]
    train(cc, xs_ct, num_layers)


if __name__ == "__main__":
    main()
