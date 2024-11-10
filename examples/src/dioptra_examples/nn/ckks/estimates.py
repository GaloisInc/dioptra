from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.decorator import dioptra_runtime

from dioptra_examples.nn import NN
from dioptra_examples.schemes import CKKS


@dioptra_runtime()
def nn_2_input_1_layer(cc: Analyzer):
    num_inputs = 2
    num_layers = 1
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]

    # Generate arbitrary nn
    neuron_weights = [i for i in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights for _ in range(num_layers)]
    nn = NN.nn_from_plaintexts(cc, CKKS(), nn_weights)

    nn.train(cc, xs_ct)
