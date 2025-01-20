import openfhe as ofhe
from dioptra.context import dioptra_pke_context
from dioptra.utils.scheme_type import SchemeType

def mk_ckks(sec_level: ofhe.SecurityLevel, ring_dimension: int = 1 << 17) -> (
    tuple[
        ofhe.CryptoContext,
        ofhe.CCParamsCKKSRNS,
        ofhe.KeyPair,
        list[ofhe.PKESchemeFeature],
    ]
):
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
    return (cryptocontext, parameters, key_pair, features)

def mk_bfv(pt_mod: int, sec_level: ofhe.SecurityLevel, mult_depth: int) -> tuple[
        ofhe.CryptoContext,
        ofhe.CCParamsCKKSRNS,
        ofhe.KeyPair,
        list[ofhe.PKESchemeFeature],
    ]:
    parameters = ofhe.CCParamsBFVRNS()
    parameters.SetSecurityLevel(sec_level)
    parameters.SetPlaintextModulus(pt_mod)
    parameters.SetMultiplicativeDepth(mult_depth)

    crypto_context = ofhe.GenCryptoContext(parameters)
    features = [
        ofhe.PKESchemeFeature.PKE,
        ofhe.PKESchemeFeature.KEYSWITCH,
        ofhe.PKESchemeFeature.LEVELEDSHE,
    ]
    for feature in features:
        crypto_context.Enable(feature)

    key_pair = crypto_context.KeyGen()

    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair, features)

def mk_bgv(pt_mod: int, sec_level: ofhe.SecurityLevel, mult_depth: int) -> tuple[
        ofhe.CryptoContext,
        ofhe.CCParamsCKKSRNS,
        ofhe.KeyPair,
        list[ofhe.PKESchemeFeature],
    ]:

    parameters = ofhe.CCParamsBGVRNS()
    parameters.SetPlaintextModulus(pt_mod)
    parameters.SetMultiplicativeDepth(mult_depth)
    parameters.SetSecurityLevel(sec_level)

    crypto_context = ofhe.GenCryptoContext(parameters)

    features = [
        ofhe.PKESchemeFeature.PKE,
        ofhe.PKESchemeFeature.KEYSWITCH,
        ofhe.PKESchemeFeature.LEVELEDSHE,
    ]
    for feature in features:
        crypto_context.Enable(feature)

    key_pair = crypto_context.KeyGen()

    crypto_context.EvalMultKeyGen(key_pair.secretKey)
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    return (crypto_context, parameters, key_pair, features)

def mk_binfhe(pset: ofhe.BINFHE_PARAMSET = ofhe.STD128, method: ofhe.BINFHE_METHOD = ofhe.GINX):
    cc = ofhe.BinFHEContext()
    cc.GenerateBinFHEContext(pset, method)
    sk = cc.KeyGen()
    cc.BTKeyGen(sk)

    return (cc, sk)
