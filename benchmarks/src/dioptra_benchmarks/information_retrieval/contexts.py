from dioptra.context import dioptra_binfhe_context, dioptra_pke_context
import openfhe as ofhe
import benchmark.contexts as ctxts


def mk_bfv_evalsum(pt_mod: int, sec_level: ofhe.SecurityLevel, mult_depth: int) -> tuple[
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
        ofhe.PKESchemeFeature.ADVANCEDSHE,
    ]
    for feature in features:
        crypto_context.Enable(feature)

    key_pair = crypto_context.KeyGen()

    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

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

@dioptra_pke_context()
def bfv_128():
  return mk_bfv_evalsum(pt_mod=65537, sec_level=ofhe.SecurityLevel.HEStd_128_classic, mult_depth=3)

@dioptra_binfhe_context()
def binfhe_128():
  return ctxts.mk_binfhe()

contexts = {
  "bfv_128": bfv_128,
  "bgv_128": bgv_128,
  "binfhe_128": binfhe_128,
}
