import openfhe as ofhe
from contexts import bgv1

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
class Scheme: 
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        raise NotImplementedError("Plaintext packing is not implemented for this scheme")
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        raise NotImplementedError("The zero value is not implemented for this scheme")
    def bootstrap(self, cc: ofhe.CryptoContext, level: int, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        pass

class CKKS(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext([0.0])
    def bootstrap(self, cc: ofhe.CryptoContext,  value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return cc.EvalBootstrap(value) 

class BFV(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
       return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return value

class BGV(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        #OpenFHE does not support boostrapping for BGV
        return value

class Neuron:
    def __init__(
        self, 
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        weights: list[ofhe.Ciphertext], 
        bias = None,
    ) -> Self:
        self.scheme = scheme
        self.num_inputs = len(weights)
        self.weights = weights

        if bias is None:
            self.bias = self.scheme.zero(cc)
        else:
            self.bias = bias

    def set_id(self, neuron_id: int):
        self.neuron_id = neuron_id

    def set_bias(self, bias: ofhe.Ciphertext):
        self.bias = bias

    def neuron_from_plaintext(cc: ofhe.CryptoContext, scheme: Scheme, weights: list[int], bias = None) -> Self:
        weights_ckks = []
        for w in weights:
            weights_ckks.append(scheme.make_plaintext(cc, [w]))
        return Neuron(cc, scheme, weights_ckks, bias)

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
        scheme: Scheme, 
        neurons: list[Neuron],
        bias = None,
    ) -> Self:
        self.num_neuron = len(neurons)
        self.scheme = scheme
        for i, neuron in enumerate(neurons):
            neuron.set_id(i)   
            if bias != None:
                neuron.set_bias(bias)      
        self.neurons = neurons

    def set_id(self, layer_id: int):
        self.layer_id = layer_id

    def layer_from_plaintexts(cc: ofhe.CryptoContext, scheme: Scheme, weights_layer: list[list[int]], bias = None) -> Self:
        neurons = []
        for weights_neuron in weights_layer:
            neuron = Neuron.neuron_from_plaintext(cc, scheme, weights_neuron, bias)
            neurons.append(neuron)
        return Layer(cc, scheme, neurons, bias)

    def bootstrap(self, cc: ofhe.CryptoContext, inputs: list[ofhe.Ciphertext]) -> list[ofhe.Ciphertext]:
         return [self.scheme.bootstrap(cc, input) for input in inputs]   
        
    def train(
        self, 
        cc: ofhe.CryptoContext, 
        inputs: list[ofhe.Ciphertext]
        ) -> list[ofhe.Ciphertext]:
        self.check_correctness(len(inputs))

        layer_out = []
        for i, neuron in enumerate(self.neurons):
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
        scheme: Scheme, 
        layers: list[Layer],
    ) -> Self:
        self.num_layers = len(layers)
        self.scheme = scheme
        for i, layer in enumerate(layers):
            layer.set_id(i)
        self.layers = layers

    def nn_from_plaintexts(cc: ofhe.CryptoContext, scheme: Scheme, weights_nn: list[list[list[float]]], bias = None) -> Self:
        layers = []
        for weights_layer in weights_nn:
            layer = Layer.layer_from_plaintexts(cc, scheme, weights_layer)
            layers.append(layer)
        return NN(cc, scheme, layers)

    def train(
        self,
        cc: ofhe.CryptoContext,
        inputs: list[ofhe.Ciphertext]
    ) -> ofhe.Ciphertext:
        layer_input = inputs
        for i, layer in enumerate(self.layers):
            layer_input = layer.train(cc, layer_input)
            if i % 5 == 0:
                layer_input = layer.bootstrap(cc, layer_input)
        return layer_input

# Actually run program and time it
def main():
    num_inputs = 2
    num_layers = 1
    (cc, parameters, key_pair, _) = bgv1()

    # encode and encrypt inputs labels
    xs = [[i] for i in range(num_inputs)]
    xs_pt = [cc.MakePackedPlaintext(x) for x in xs]
    for x in xs_pt:
        x.SetLength(1)
    xs_ct = [cc.Encrypt(key_pair.publicKey, x_pt) for x_pt in xs_pt]

    # Generate arbitrary nn 
    neuron_weights = [i for i in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights for _ in range(num_layers)]
    nn = NN.nn_from_plaintexts(cc, BGV(), nn_weights)

    # time and run the program
    start_ns = time_ns()
    results = nn.train(cc, xs_ct)
    end_ns = time_ns()

    results_unpacked = []
    for r in results:
        result = cc.Decrypt(key_pair.secretKey, r)
        result.SetLength(1)
        results_unpacked.append(result.GetPackedValue())
    print(results_unpacked)

    print(f"Actual runtime: {format_ns(end_ns - start_ns)}")


@dioptra_runtime()
def report_runtime(cc: Analyzer):
    num_inputs = 11
    num_layers = 5
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]

    # Generate arbitrary nn 
    neuron_weights = [i for i in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights for _ in range(num_layers)]
    
    nn = NN.nn_from_plaintexts(cc, BGV(), nn_weights)

    nn.train(cc, xs_ct)


if __name__ == "__main__":
    main()
