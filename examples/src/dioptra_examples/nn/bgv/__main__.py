import time

from dioptra.analyzer.utils.util import format_ns

from dioptra_examples.contexts import bgv1
from dioptra_examples.nn import NN
from dioptra_examples.schemes import BGV

# Actually train a neural network and time it.
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
start_ns = time.time_ns()
results = nn.train(cc, xs_ct)
end_ns = time.time_ns()

# decrypt the results
results_unpacked = []
for r in results:
    result = cc.Decrypt(key_pair.secretKey, r)
    result.SetLength(1)
    results_unpacked.append(result.GetPackedValue())
print(results_unpacked)

print(f"Actual runtime: {format_ns(end_ns - start_ns)}")
