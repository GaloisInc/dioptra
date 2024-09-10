import openfhe as ofhe

from dioptra.decorator import dioptra_binfhe_context, dioptra_context

@dioptra_context()
def ckks1() -> tuple[ofhe.CryptoContext, ofhe.CCParamsCKKSRNS, ofhe.KeyPair, list[ofhe.PKESchemeFeature]]:
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
    return (cryptocontext, parameters, key_pair, features)

@dioptra_context()
def bfv1() -> tuple[ofhe.CryptoContext, ofhe.CCParamsBFVRNS, ofhe.KeyPair, list[ofhe.PKESchemeFeature]]:
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBFVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)

    crypto_context = ofhe.GenCryptoContext(parameters)
    # Enable features that you wish to use
    features = [ofhe.PKESchemeFeature.PKE, ofhe.PKESchemeFeature.KEYSWITCH, ofhe.PKESchemeFeature.LEVELEDSHE]
    for feature in features:
        crypto_context.Enable(feature)

    # Step 2: Key Generation

    # Generate a public/private key pair
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair, features)

@dioptra_context()
def bgv1() -> tuple[ofhe.CryptoContext, ofhe.CCParamsBGVRNS, ofhe.KeyPair, list[ofhe.PKESchemeFeature]]:
    # Sample Program: Step 1: Set CryptoContext
    parameters = ofhe.CCParamsBGVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)

    crypto_context = ofhe.GenCryptoContext(parameters)
    # Enable features that you wish to use
    features = [ofhe.PKESchemeFeature.PKE, ofhe.PKESchemeFeature.KEYSWITCH, ofhe.PKESchemeFeature.LEVELEDSHE]
    for feature in features:
        crypto_context.Enable(feature)

    # Sample Program: Step 2: Key Generation

    # Generate a public/private key pair
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair, features)


@dioptra_binfhe_context()
def binfhe1():
    cc = ofhe.BinFHEContext()
    cc.GenerateBinFHEContext(ofhe.STD128,ofhe.GINX)
    sk = cc.KeyGen()
    cc.BTKeyGen(sk)

    return (cc, sk)


def bfv_mult():
    (cc, _, kp, _) = bfv1()
    def mkct(v):
        pt = cc.MakePackedPlaintext(v)
        return cc.Encrypt(kp.publicKey, pt)
    
    def mul_lv(c1, c2, s):
        result = cc.EvalMult(c1, c2)
        print(f"{s} -- arg1 level: {c1.GetLevel()}  arg2 level: {c2.GetLevel()}  result level: {result.GetLevel()}")
        return result
    
    c1 = mkct([1,2,3,4])
    c2 = mkct([3,2,1,4])
    c3 = mkct([5,3,4,5])

    r = mul_lv(c1, c2, "r = c1 * c2")
    r2 = mul_lv(r, c3, "r2 = r * c3")
    r3 = mul_lv(r2, r2, "r3 = r2 * r2")
