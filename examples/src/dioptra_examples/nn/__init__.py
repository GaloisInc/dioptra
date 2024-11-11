"""Simple neural network in FHE.

Implements only forward propagations, and supports any number of neurons.
"""

from functools import reduce
from typing import Self

import openfhe as ofhe

from dioptra_examples.schemes import Scheme


def activation(cc: ofhe.CryptoContext, input: ofhe.Ciphertext) -> ofhe.Ciphertext:
    """Square is used as a linear approximation of an axtivation function."""
    return cc.EvalMult(input, input)


class Neuron:
    """Defines the behavior of a Neuron

    We assume that the neurons in the NN are strongly connected,
    i.e. if an edge does not contribute to the input weight of a
    neuron should be set to 0.
    """

    def __init__(
        self,
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        weights: list[ofhe.Ciphertext],
        bias=None,
    ):
        self.scheme = scheme
        self.num_inputs = len(weights)
        self.weights = weights

        if bias is None:
            self.bias = self.scheme.zero(cc)
        else:
            self.bias = bias

    def set_id(self, neuron_id: int):
        """Helper function that sets the id of a neuron

        This is used for book-keeping and debugging"""
        self.neuron_id = neuron_id

    def set_bias(self, bias: ofhe.Ciphertext):
        self.bias = bias

    @classmethod
    def neuron_from_plaintext(
        cls,
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        weights: list[int | float],
        bias=None,
    ) -> Self:
        """Helper function that creates a neuron from a list of plaintexts"""
        weights_ckks = []
        for w in weights:
            weights_ckks.append(scheme.make_plaintext(cc, [w]))
        return cls(cc, scheme, weights_ckks, bias)

    def train(
        self, cc: ofhe.CryptoContext, inputs: list[ofhe.Ciphertext]
    ) -> ofhe.Ciphertext:
        if len(inputs) != self.num_inputs:
            raise ValueError(
                f"The number of inputs {len(inputs)} does not match the number of neuron inputs {self.num_inputs}"
            )

        mults = map(lambda x, y: cc.EvalMult(x, y), inputs, self.weights)
        sum = reduce(lambda x, y: cc.EvalAdd(x, y), mults)
        sum = cc.EvalAdd(sum, self.bias)
        return activation(cc, sum)


class Layer:
    """Defines the behavior of a Layer"""

    def __init__(
        self,
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        neurons: list[Neuron],
        bias=None,
    ):
        self.num_neuron = len(neurons)
        self.scheme = scheme
        for i, neuron in enumerate(neurons):
            neuron.set_id(i)
            if bias is not None:
                neuron.set_bias(bias)
        self.neurons = neurons

    def set_id(self, layer_id: int):
        self.layer_id = layer_id

    @classmethod
    def layer_from_plaintexts(
        cls,
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        weights_layer: list[list[int | float]],
        bias=None,
    ) -> Self:
        """Helper function that creates a layer from a list of plaintexts"""
        neurons = []
        for weights_neuron in weights_layer:
            neuron = Neuron.neuron_from_plaintext(cc, scheme, weights_neuron, bias)
            neurons.append(neuron)
        return cls(cc, scheme, neurons, bias)

    def bootstrap(
        self, cc: ofhe.CryptoContext, inputs: list[ofhe.Ciphertext]
    ) -> list[ofhe.Ciphertext]:
        """Insert a bootstrapping layers into the NN that bootstraps every output of the prior layer if the scheme requires it"""
        return [self.scheme.bootstrap(cc, input) for input in inputs]

    def train(
        self, cc: ofhe.CryptoContext, inputs: list[ofhe.Ciphertext]
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
        for neuron in self.neurons:
            assert (
                num_inputs == neuron.num_inputs
            ), f"On Layer #{self.layer_id}: Number of inputs{num_inputs} != Indegree of Neuron #{neuron.neuron_id} is {neuron.num_inputs}"


class NN:
    def __init__(
        self,
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        layers: list[Layer],
    ):
        self.num_layers = len(layers)
        self.scheme = scheme
        for i, layer in enumerate(layers):
            layer.set_id(i)
        self.layers = layers

    @classmethod
    def nn_from_plaintexts(
        cls,
        cc: ofhe.CryptoContext,
        scheme: Scheme,
        weights_nn: list[list[list[int | float]]],
        bias=None,
    ) -> Self:
        # propagate the output of the prior layer into
        # the current layer and train it
        layers = []
        for weights_layer in weights_nn:
            layer = Layer.layer_from_plaintexts(cc, scheme, weights_layer)
            layers.append(layer)
        return cls(cc, scheme, layers)

    def train(
        self, cc: ofhe.CryptoContext, inputs: list[ofhe.Ciphertext]
    ) -> ofhe.Ciphertext:
        layer_input = inputs
        for i, layer in enumerate(self.layers):
            layer_input = layer.train(cc, layer_input)
            # Add a bootstrapping layer after every 5th layer
            # if the scheme requires it
            if i % 5 == 0:
                layer_input = layer.bootstrap(cc, layer_input)
        return layer_input
