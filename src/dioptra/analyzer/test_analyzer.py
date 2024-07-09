
from analyzer_context import *

def runexample(fun) -> None:#type: ignore
    md = MultDepth()
    analyzer = Analyzer([md])
    fun(analyzer)
    print(f"Max Depth: {md.max_depth}")
    print(f"Where Depths: {md.where}")
    md.anotate_depth()

def square(crypto_context: Analyzer, c1: Ciphertext) -> Ciphertext:
    return crypto_context.EvalMult(c1, c1)

@runexample
def example(crypto_context: Analyzer) -> None:
    key_pair = crypto_context.KeyGen()

    # Generate the relinearization key
    crypto_context.EvalMultKeyGen(key_pair.secretKey)

    # Generate the rotation evaluation keys
    crypto_context.EvalRotateKeyGen(key_pair.secretKey, [1, 2, -1, -2])

    # Sample Program: Step 3: Encryption

    # First plaintext vector is encoded
    vector_of_ints1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    plaintext1 = crypto_context.MakePackedPlaintext(vector_of_ints1)

    # Second plaintext vector is encoded
    vector_of_ints2 = [3, 2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    plaintext2 = crypto_context.MakePackedPlaintext(vector_of_ints2)

    # The encoded vectors are encrypted
    ciphertext1 = crypto_context.Encrypt(key_pair.publicKey, plaintext1)
    ciphertext2 = crypto_context.Encrypt(key_pair.publicKey, plaintext2)

    v = crypto_context.EvalMult(ciphertext1, ciphertext2)
    v2 = crypto_context.EvalMult(v, v)
    _v3 = crypto_context.EvalMult(v, v2)
    _v4 = crypto_context.EvalMult(ciphertext1, ciphertext1) 
    _v6 = square(crypto_context, v)
    _v7 = square(crypto_context, _v6)