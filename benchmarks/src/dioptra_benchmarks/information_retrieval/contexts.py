from dioptra.context import dioptra_binfhe_context, dioptra_pke_context
import openfhe as ofhe
import benchmark.contexts as ctxts

# in the case of PKE, we need contexts for this that can run evalsum
# which is why slightly similar contexts (wrt benchmark/contexts.py) have been defined here 

@dioptra_pke_context()
def ckks_128() -> (
    tuple[
        ofhe.CryptoContext,
        ofhe.CCParamsCKKSRNS,
        ofhe.KeyPair,
        list[ofhe.PKESchemeFeature],
    ]
):
    sec_level: ofhe.SecurityLevel = ofhe.SecurityLevel.HEStd_128_classic
    ring_dimension: int = 1 << 17
    parameters = ofhe.CCParamsCKKSRNS()

    secret_key_dist = ofhe.SecretKeyDist.UNIFORM_TERNARY
    parameters.SetSecretKeyDist(secret_key_dist)

    parameters.SetSecurityLevel(sec_level)
    parameters.SetRingDim(ring_dimension)

    if ofhe.get_native_int() == 128:
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

    depth = levels_available_after_bootstrap + ofhe.FHECKKSRNS.GetBootstrapDepth(
        level_budget, secret_key_dist
    )

    parameters.SetMultiplicativeDepth(depth)

    cryptocontext = ofhe.GenCryptoContext(parameters)

    features = [
        ofhe.PKESchemeFeature.PKE,
        ofhe.PKESchemeFeature.KEYSWITCH,
        ofhe.PKESchemeFeature.LEVELEDSHE,
        ofhe.PKESchemeFeature.ADVANCEDSHE,
        ofhe.PKESchemeFeature.FHE,
    ]

    for feature in features:
        cryptocontext.Enable(feature)

    cryptocontext.EvalBootstrapSetup(level_budget)

    key_pair = cryptocontext.KeyGen()
    cryptocontext.EvalMultKeyGen(key_pair.secretKey)
    cryptocontext.EvalBootstrapKeyGen(key_pair.secretKey, parameters.GetRingDim() >> 1)
    cryptocontext.EvalSumKeyGen(key_pair.secretKey)
    return (cryptocontext, parameters, key_pair, features)

@dioptra_pke_context()
def bfv_128() -> tuple[
        ofhe.CryptoContext,
        ofhe.CCParamsCKKSRNS,
        ofhe.KeyPair,
        list[ofhe.PKESchemeFeature],
    ]:
    sec_level: ofhe.SecurityLevel = ofhe.SecurityLevel.HEStd_128_classic
    mult_depth: int = 3
    pt_mod = 65537
    parameters = ofhe.CCParamsBFVRNS()
    parameters.SetSecurityLevel(sec_level)
    parameters.SetPlaintextModulus(pt_mod)
    parameters.SetMultiplicativeDepth(mult_depth)

    crypto_context = ofhe.GenCryptoContext(parameters)
    features = [
        ofhe.PKESchemeFeature.PKE,
        ofhe.PKESchemeFeature.KEYSWITCH,
        ofhe.PKESchemeFeature.LEVELEDSHE,
        ofhe.PKESchemeFeature.ADVANCEDSHE,
    ]
    for feature in features:
        crypto_context.Enable(feature)

    key_pair = crypto_context.KeyGen()

    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    crypto_context.EvalSumKeyGen(key_pair.secretKey)

    return (crypto_context, parameters, key_pair, features)


@dioptra_pke_context()
def bgv_128() -> (
    tuple[
        ofhe.CryptoContext,
        ofhe.CCParamsBGVRNS,
        ofhe.KeyPair,
        list[ofhe.PKESchemeFeature],
    ]
):
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBGVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(3)
    parameters.SetSecurityLevel(ofhe.SecurityLevel.HEStd_128_classic)

    crypto_context = ofhe.GenCryptoContext(parameters)
    # Enable features that you wish to use
    features = [
        ofhe.PKESchemeFeature.PKE,
        ofhe.PKESchemeFeature.KEYSWITCH,
        ofhe.PKESchemeFeature.LEVELEDSHE,
        ofhe.PKESchemeFeature.ADVANCEDSHE
    ]
    for feature in features:
        crypto_context.Enable(feature)

    # Sample Program: Step 2: Key Generation

    # Generate a public/private key pair
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [-2,-1,1,2])

    crypto_context.EvalSumKeyGen(key_pair.secretKey)

    return (crypto_context, parameters, key_pair, features)


@dioptra_binfhe_context()
def binfhe_128():
  return ctxts.mk_binfhe()

contexts = {
  "bfv_128": bfv_128,
  "bgv_128": bgv_128,
  "binfhe_128": binfhe_128,
  "ckks_128": ckks_128,
}

def is_binfhe(ctx: str) -> bool:
    return ctx == "binfhe_128"

def is_ckks(ctx: str) -> bool:
    return ctx == "ckks_128"
