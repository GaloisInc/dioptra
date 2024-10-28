""" Simple Neural Network in BGV

This example implements a simple neural network in BGV.
This example only implementes forward propagations and supports
varying numbers of neurons.
"""
import openfhe as ofhe
from contexts import bgv1
from schemes import Scheme

from time import time_ns
from random import random
from functools import reduce
from typing import Self


from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime

def nn_activation(cc: ofhe.CryptoContext, input: ofhe.Ciphertext):
    # We consider the square as a linear approximation of an 
    # activation function
    return cc.EvalMult(input, input)

class BGV(Scheme):
    """Class which defines BGV specific behavior"""
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        #OpenFHE does not support boostrapping for BGV
        return value

class Neuron:
    """ Defines the behavior of a Neuron
    
    We assume that the neurons in the NN are strongly connected, 
    i.e. if an edge does not contribute to the input weight of a 
    neuron should be set to 0.
    """
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
        # Helper function that sets the id of a neuron
        # This is used for book-keeping and debugging
        self.neuron_id = neuron_id

    def set_bias(self, bias: ofhe.Ciphertext):
        self.bias = bias

    def neuron_from_plaintext(cc: ofhe.CryptoContext, scheme: Scheme, weights: list[int], bias = None) -> Self:
        # Helper function that creates a neuron from a list of plaintexts
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
        # The inputs are multiplied with the weights
        mults = map(lambda x, y: cc.EvalMult(x,y), inputs, self.weights)
        # The results are then aggregated
        sum = reduce(lambda x, y: cc.EvalAdd(x,y), mults)
        # The bias if it exists is added to the sum
        sum = cc.EvalAdd(sum, self.bias)
        # The result is activated
        return nn_activation(cc, sum)

class Layer:
    """ Defines the behavior of a Layer
    """
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
        # Helper function that creates a layer from a list of plaintexts
        neurons = []
        for weights_neuron in weights_layer:
            neuron = Neuron.neuron_from_plaintext(cc, scheme, weights_neuron, bias)
            neurons.append(neuron)
        return Layer(cc, scheme, neurons, bias)

    def bootstrap(self, cc: ofhe.CryptoContext, inputs: list[ofhe.Ciphertext]) -> list[ofhe.Ciphertext]:
         # Insert a bootstrapping layers into the NN that bootstraps every output of 
         # the prior layer if the scheme requires it
         return [self.scheme.bootstrap(cc, input) for input in inputs]   
        
    def train(
        self, 
        cc: ofhe.CryptoContext, 
        inputs: list[ofhe.Ciphertext]
        ) -> list[ofhe.Ciphertext]:
        self.check_correctness(len(inputs))

        layer_out = []
        # propagate the output of the prior layer's neurons into
        # the current layer's neurons and train it
        for i, neuron in enumerate(self.neurons):
            neuron_out = neuron.train(cc, inputs)
            layer_out.append(neuron_out)
        return layer_out

    def check_correctness(self, num_inputs: int):
        # Helper function that makes sure tha the number of incoming
        # inputs matches the number of neurons. The neurons in the NN
        # are strongly connected, i.e. if an edge does not contribute
        # to the input weight of a neuron should be set to 0.
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
        # propagate the output of the prior layer into
        # the current layer and train it
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
            # Add a bootstrapping layer after every 5th layer
            # if the scheme requires it
            if i % 5 == 0:
                layer_input = layer.bootstrap(cc, layer_input)
        return layer_input

# Actually run program and time it
def main():
    num_inputs = 10
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

    # decrypt the results
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
