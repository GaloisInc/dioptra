import openfhe as ofhe

from dioptra.decorator import dioptra_context

@dioptra_context()
def mk_ckks1_with_keypair() -> tuple[ofhe.CryptoContext, ofhe.CCParamsCKKSRNS, ofhe.KeyPair]:
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

    key_pair = cryptocontext.KeyGen()
    cryptocontext.EvalMultKeyGen(key_pair.secretKey)
    cryptocontext.EvalBootstrapKeyGen(key_pair.secretKey, parameters.GetRingDim() >> 1)
    return (cryptocontext, parameters, key_pair)

@dioptra_context()
def mk_bfv1() -> tuple[ofhe.CryptoContext, ofhe.CCParamsBFVRNS, ofhe.KeyPair]:
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBFVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)

    crypto_context = ofhe.GenCryptoContext(parameters)
    # Enable features that you wish to use
    crypto_context.Enable(ofhe.PKESchemeFeature.PKE)
    crypto_context.Enable(ofhe.PKESchemeFeature.KEYSWITCH)
    crypto_context.Enable(ofhe.PKESchemeFeature.LEVELEDSHE)

    # Step 2: Key Generation

    # Generate a public/private key pair
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair)

@dioptra_context()
def mk_bgv1() -> tuple[ofhe.CryptoContext, ofhe.CCParamsBGVRNS, ofhe.KeyPair]:
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBGVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)

    crypto_context = ofhe.GenCryptoContext(parameters)
    # Enable features that you wish to use
    crypto_context.Enable(ofhe.PKESchemeFeature.PKE)
    crypto_context.Enable(ofhe.PKESchemeFeature.KEYSWITCH)
    crypto_context.Enable(ofhe.PKESchemeFeature.LEVELEDSHE)

    # Sample Program: Step 2: Key Generation

    # Generate a public/private key pair
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair)
