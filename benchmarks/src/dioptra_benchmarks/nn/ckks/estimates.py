from dioptra.estimate import dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer
from dioptra_examples.nn import NN
from dioptra_examples.schemes import CKKS

import random

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

    nn.train(cc, xs_ct)
