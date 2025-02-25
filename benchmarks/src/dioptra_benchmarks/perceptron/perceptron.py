
from benchmark.common import DisplayTime
from dioptra.pke.analyzer import Analyzer, Ciphertext, Plaintext
from openfhe import CryptoContext
import context

import random

# Class representing a single perceptron
class Perceptron:
    # Initialize perceptron
    def __init__(self, weights: list[Plaintext], bias: Plaintext|None = None):
        self.weights = weights  # weights of the inputs
        self.bias = bias        # output bias

    # Run the perceptron with the current weights
    def classify(self, cc: Analyzer, input: list[Ciphertext]) -> Ciphertext:
        sum = None
        for i in range(len(self.weights)):
            w = cc.EvalMult(input[i], self.weights[i])
            if sum is None:
                sum = w
            else:
                sum = cc.EvalAdd(sum, w)

        if self.bias is not None:
            sum = cc.EvalAdd(self.bias, sum)

        # Acrivation function
        return cc.EvalMult(sum, sum)

# Run a single perceptron using the `ckks1` context from `dioptra_examples`
# Outputs labelled runtimes - the last of which is the same runtime as should
# be estimated by the estimator
def run_single_perception_cc(input_size: int):
    cc = None
    with DisplayTime("setup") as _:
        (cc, _, kp, _) = context.ckks_128()

    inputs = []
    with DisplayTime("encrypt") as _:
        for _ in range(input_size):
            n = random.uniform(0, 1)
            pt = cc.MakeCKKSPackedPlaintext([n])
            inputs.append(cc.Encrypt(kp.publicKey, pt))

    with DisplayTime("runtime") as _:
        run_single_perceptron(cc, inputs)

# NB: this also includes the encoding time for the perceptron weights, which could
#     possibly be omitted if you just want to compare running the perceptrons
def run_single_perceptron(cc: Analyzer|CryptoContext, inputs: list[Ciphertext]):
    weights = [cc.MakeCKKSPackedPlaintext([random.uniform(0, 1)]) for i in range(len(inputs))]
    p = Perceptron(weights)
    p.classify(cc, inputs)

def mk_estimate_input(cc: Analyzer, i: int):
    return [cc.ArbitraryCT() for _ in range(i)]