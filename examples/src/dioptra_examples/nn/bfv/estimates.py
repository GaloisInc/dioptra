from dioptra.estimate import dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer
from dioptra_examples.nn import NN
from dioptra_examples.schemes import BFV


@dioptra_pke_estimation()
def nn_11_input_5_layer(cc: Analyzer):
    num_inputs = 11
    num_layers = 5
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]

    # Generate arbitrary nn
    neuron_weights = [i for i in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights for _ in range(num_layers)]
    nn = NN.nn_from_plaintexts(cc, BFV(), nn_weights)

    nn.classify(cc, xs_ct)
