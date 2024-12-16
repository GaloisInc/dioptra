from functools import reduce
import sys
import time
import dioptra
from dioptra.estimate import dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer, Ciphertext, Plaintext
from dioptra_examples.contexts import ckks1
from openfhe import CryptoContext

import random
import dioptra.utils.measurement

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

# Class for displaying runtime of a chunk of code
# To be used with python's `with` syntax
class DisplayTime:
    def __init__(self, p: str):
        self.p = p

    def __enter__(self):
        self.start = time.time_ns()
        return self

    def __exit__(self, *arg):
        end = time.time_ns()
        print(f"{self.p}: {dioptra.utils.measurement.format_ns_approx(end - self.start)}")

# Run a single perceptron using the `ckks1` context from `dioptra_examples`
# Outputs labelled runtimes - the last of which is the same runtime as should
# be estimated by the estimator
def run_single_perception_cc(input_size: int):
    cc = None
    with DisplayTime("setup") as _:
        (cc, _, kp, _) = ckks1()

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

# Estimation cases
@dioptra_pke_estimation()
def single_perceptron_classify_10(cc: Analyzer):
    run_single_perceptron(cc, mk_estimate_input(cc, 10))

@dioptra_pke_estimation()
def single_perceptron_classify_50(cc: Analyzer):
    run_single_perceptron(cc, mk_estimate_input(cc, 50))

@dioptra_pke_estimation()
def single_perceptron_classify_100(cc: Analyzer):
    run_single_perceptron(cc, mk_estimate_input(cc, 100))

# Runner to test actual runtime against
def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} NUMBER")
        sys.exit(1)
    i = int(sys.argv[1])
    run_single_perception_cc(i)

if __name__ == "__main__":
    main()