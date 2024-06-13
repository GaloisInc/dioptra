from openfhe import *

# Sample Program: Step 1: Set CryptoContext
parameters = CCParamsBFVRNS()
parameters.SetPlaintextModulus(65537)
parameters.SetMultiplicativeDepth(0)

crypto_context = GenCryptoContext(parameters)
# Enable features that you wish to use
crypto_context.Enable(PKESchemeFeature.PKE)
crypto_context.Enable(PKESchemeFeature.LEVELEDSHE)

# Sample Program: Step 2: Key Generation

# Generate a public/private key pair
key_pair = crypto_context.KeyGen()

pt1 = crypto_context.MakePackedPlaintext([3])
pt2 = crypto_context.MakePackedPlaintext([2])

# The encoded vectors are encrypted
ct1 = crypto_context.Encrypt(key_pair.publicKey, pt1)
ct2 = crypto_context.Encrypt(key_pair.publicKey, pt2)


ctADD = crypto_context.EvalAdd(ct1, ct2)

result = crypto_context.Decrypt(key_pair.secretKey, ctADD)

print(f"Result of encrypted computation of 2 + 3 = {result}")
