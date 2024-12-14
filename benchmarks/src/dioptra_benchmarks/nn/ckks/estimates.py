from dioptra.estimate import dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer
from dioptra_examples.nn import NN, Neuron
from dioptra_examples.schemes import CKKS

import random


def run_single_perceptron(cc: Analyzer, input_len: int):
    weights = [cc.MakeCKKSPackedPlaintext([random.uniform(0, 1)]) for i in range(input_len)]
    inputs = [cc.ArbitraryCT() for i in range(input_len)]
    p = Neuron(cc, CKKS(), weights, None)
    p.classify(cc, inputs)

@dioptra_pke_estimation()
def single_perceptron_classify_10(cc: Analyzer):
    run_single_perceptron(cc, 10)

@dioptra_pke_estimation()
def single_perceptron_classify_100(cc: Analyzer):
    run_single_perceptron(cc, 100)

@dioptra_pke_estimation()
def single_perceptron_classify_1000(cc: Analyzer):
    run_single_perceptron(cc, 1000)

@dioptra_pke_estimation()
def nn_1_input_3_layer(cc: Analyzer):
    num_inputs = 1
    num_layers = 2
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]

    # Generate arbitrary nn
    neuron_weights = [random.uniform(0, 1) for i in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights for _ in range(num_layers)]
    nn = NN.nn_from_plaintexts(cc, CKKS(), nn_weights)

    nn.classify(cc, xs_ct)
