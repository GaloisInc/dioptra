from dioptra.pke.analyzer import Analyzer
from dioptra_benchmarks.perceptron import *


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
