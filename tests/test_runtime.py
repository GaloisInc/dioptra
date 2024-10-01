from dioptra.analyzer.pke.analysisbase import Analyzer, Value, Ciphertext, Plaintext
from dioptra.analyzer.pke.multdepth import MultDepth
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.calibration import PKECalibrationData, format_ns
import openfhe
import time

def runestimator(fun) -> None:#type: ignore
    # Read runtime table of each FHE operation
    runtime_samples_file = "src/dioptra/analyzer/balanced.samples"
    runtime_table = PKECalibrationData()
    runtime_table.read_json(runtime_samples_file)

    # Run the multiplicative depth analyzer first
    rt = Runtime(runtime_table)
    analyzer = Analyzer([rt])
    fun(analyzer)
    print(f"Total Runtime: {rt.total_runtime} ns")
    rt.anotate_metric()

def square(cryptocontext: Analyzer, c1: Ciphertext) -> Ciphertext:
    return cryptocontext.EvalMult(c1, c1)

# @runestimator
def example():
    # Setup Parameters
    parameters = openfhe.CCParamsCKKSRNS()
    secret_key_dist = openfhe.SecretKeyDist.UNIFORM_TERNARY
    parameters.SetSecretKeyDist(secret_key_dist)
    parameters.SetSecurityLevel(openfhe.SecurityLevel.HEStd_NotSet)
    parameters.SetRingDim(1 << 16)

    rescale_tech = openfhe.ScalingTechnique.FLEXIBLEAUTO

    dcrt_bits = 59
    first_mod = 60

    parameters.SetScalingModSize(dcrt_bits)
    parameters.SetScalingTechnique(rescale_tech)
    parameters.SetFirstModSize(first_mod)

    num_iterations = 2

    level_budget = [3, 3]
    depth = 10 + openfhe.FHECKKSRNS.GetBootstrapDepth(level_budget, secret_key_dist) + (num_iterations - 1)

    parameters.SetMultiplicativeDepth(depth)

    cc = openfhe.GenCryptoContext(parameters)
    cc.Enable(openfhe.PKESchemeFeature.PKE)
    cc.Enable(openfhe.PKESchemeFeature.KEYSWITCH)
    cc.Enable(openfhe.PKESchemeFeature.LEVELEDSHE)
    cc.Enable(openfhe.PKESchemeFeature.ADVANCEDSHE)
    cc.Enable(openfhe.PKESchemeFeature.FHE)

    print("Generating evaluation keys...")
    num_slots = parameters.GetRingDim() >> 1
    level_budget = [3, 3]
    bsgs_dim = [0,0]
    cc.EvalBootstrapSetup(level_budget, bsgs_dim, num_slots)

    # # key generation
    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)
    cc.EvalBootstrapKeyGen(key_pair.secretKey, num_slots)
  
    max_mult_depth = parameters.GetMultiplicativeDepth()

    start_time = time.time_ns()
    # First plaintext vector is encoded
    vector_of_ints1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    plaintext1 = cc.MakeCKKSPackedPlaintext(vector_of_ints1)

    # Second plaintext vector is encoded
    vector_of_ints2 = [3, 2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    plaintext2 = cc.MakeCKKSPackedPlaintext(vector_of_ints2)

    # The encoded vectors are encrypted
    ciphertext1 = cc.Encrypt(key_pair.publicKey, plaintext1)
    ciphertext2 = cc.Encrypt(key_pair.publicKey, plaintext2)

    v = cc.EvalMult(ciphertext1, ciphertext2)
    v2 = cc.EvalAdd(v, v)
    v3 = cc.EvalSub(v, v2)
    v4 = cc.EvalMult(v, ciphertext1) 
    v6 = square(cc, v)
    v7 = square(cc, v6)
    end_time = time.time_ns()
    print("Total Runtime without setup: " + str(format_ns(end_time - start_time)))