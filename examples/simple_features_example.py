import tempfile
import time
import openfhe as ofhe
from dioptra.analyzer.calibration import Calibration, CalibrationData
import sys

from dioptra.analyzer.metrics.analysisbase import Analyzer
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.metrics.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns

# make a cryptocontext and return the context and the parameters used to create it
def setup_context() -> tuple[ofhe.CryptoContext, ofhe.CCParamsCKKSRNS]:
    parameters = ofhe.CCParamsCKKSRNS()

    secret_key_dist = ofhe.SecretKeyDist.UNIFORM_TERNARY
    parameters.SetSecretKeyDist(secret_key_dist)

    parameters.SetSecurityLevel(ofhe.SecurityLevel.HEStd_128_classic)
    parameters.SetRingDim(1<<17)

    if ofhe.get_native_int()==128:
        rescale_tech = ofhe.ScalingTechnique.FIXEDAUTO
        dcrt_bits = 78
        first_mod = 89
    else:
        rescale_tech = ofhe.ScalingTechnique.FLEXIBLEAUTO
        dcrt_bits = 59
        first_mod = 60
    
    parameters.SetScalingModSize(dcrt_bits)
    parameters.SetScalingTechnique(rescale_tech)
    parameters.SetFirstModSize(first_mod)

    level_budget = [4, 4]

    levels_available_after_bootstrap = 10

    depth = levels_available_after_bootstrap + ofhe.FHECKKSRNS.GetBootstrapDepth(level_budget, secret_key_dist)

    parameters.SetMultiplicativeDepth(depth)

    cryptocontext = ofhe.GenCryptoContext(parameters)
    cryptocontext.Enable(ofhe.PKESchemeFeature.PKE)
    cryptocontext.Enable(ofhe.PKESchemeFeature.KEYSWITCH)
    cryptocontext.Enable(ofhe.PKESchemeFeature.LEVELEDSHE)
    cryptocontext.Enable(ofhe.PKESchemeFeature.ADVANCEDSHE)
    cryptocontext.Enable(ofhe.PKESchemeFeature.FHE)

    cryptocontext.EvalBootstrapSetup(level_budget)
    return (cryptocontext, parameters)

# A simple FHE program computing x^5 + 1
def simple_program(cc: ofhe.CryptoContext, x: ofhe.Ciphertext):
    x_pow_5 = x                           
    for i in range(0, 4):
        x_pow_5 = cc.EvalMult(x_pow_5, x)  
    one = cc.MakeCKKSPackedPlaintext([1])
    x_pow_5_1 = cc.EvalAdd(x_pow_5, one)

# calibrate runtimes for operations
# this might live as a seperate file, but we can also run it in python directly
def calibrate(outfile: str):
    (cc, params) = setup_context()
    samples = Calibration(cc, params, sys.stdout, sample_count=1).calibrate()
    samples.write_json(outfile)
    
# analyze runtime
def analyze(sample_file: str):
    # set up analyses
    depth_analysis = MultDepth()
    samples = CalibrationData()
    samples.read_json(sample_file)
    runtime_analysis = Runtime(depth_analysis, samples)
    analyzer = Analyzer([runtime_analysis])
    
    # run analysis
    x = analyzer.ArbitraryCT(level=0)     # make an arbitrary CT
    simple_program(analyzer, x)
    print(f"Estimated runtime: {format_ns(runtime_analysis.total_runtime)}")
    runtime_analysis.anotate_metric()

# Actually run program and time it
def main():
    (cc, _) = setup_context()

    # do some additional setup for openfhe that is key dependent
    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)

    # encode and encrypt input
    x = [i for i in range(0, 2 ** 16)]
    x_pt = cc.MakeCKKSPackedPlaintext(x)
    x_ct = cc.Encrypt(key_pair.publicKey, x_pt)

    # time and run the program
    start_ns = time.time_ns()
    simple_program(cc, x_ct)
    end_ns = time.time_ns()
    print(f"Actual runtime: {format_ns(end_ns - start_ns)}")
