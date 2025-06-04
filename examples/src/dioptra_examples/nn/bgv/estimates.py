from dioptra.estimate import dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer
from dioptra_examples.nn import NN
from dioptra_examples.schemes import BGV


@dioptra_pke_estimation()
def nn_10_input_1_layer(cc: Analyzer):
    num_inputs = 10
    num_layers = 1
    xs_ct = [cc.ArbitraryCT() for _ in range(num_inputs)]

    # Generate arbitrary nn
    neuron_weights = [i for i in range(num_inputs)]
    layer_weights = [neuron_weights for _ in range(num_inputs)]
    nn_weights = [layer_weights for _ in range(num_layers)]
    nn = NN.nn_from_plaintexts(cc, BGV(), nn_weights)

    nn.classify(cc, xs_ct)
