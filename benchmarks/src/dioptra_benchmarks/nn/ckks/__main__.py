import time
import random

from dioptra.utils.measurement import format_ns
from dioptra_examples.contexts import ckks1
from dioptra_examples.nn import NN
from dioptra_examples.schemes import CKKS

# Actually train a neural network and time it.
num_inputs = 1
num_layers = 3
(cc, parameters, key_pair, _) = ckks1()

# encode and encrypt inputs labels
xs = [[random.uniform(0, 1)] for i in range(num_inputs)]
xs_pt = [cc.MakeCKKSPackedPlaintext(x) for x in xs]
for x in xs_pt:
    x.SetLength(1)
xs_ct = [cc.Encrypt(key_pair.publicKey, x_pt) for x_pt in xs_pt]

# Generate arbitrary nn
neuron_weights = [random.uniform(0, 1) for _ in range(num_inputs)]
layer_weights = [neuron_weights for _ in range(num_inputs)]
nn_weights = [layer_weights for _ in range(num_layers)]
nn = NN.nn_from_plaintexts(cc, CKKS(), nn_weights)

# time and run the program
start_ns = time.time_ns()
results = nn.train(cc, xs_ct)
end_ns = time.time_ns()

# decrypt the results
results_unpacked = []
for r in results:
    result = cc.Decrypt(key_pair.secretKey, r)
    result.SetLength(1)
    results_unpacked.append(result.GetCKKSPackedValue())
print(results_unpacked)

print(f"Actual runtime: {format_ns(end_ns - start_ns)}")
