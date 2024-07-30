from dioptra.analyzer.metrics.analysisbase import Analyzer, Ciphertext
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.metrics.runtime import Runtime

def runexample(fun) -> None:#type: ignore
    runtime_table = {("mult_ctct", 1): 1, ("mult_ctct", 2): 2, ("mult_ctct", 3): 3,  ("mult_ctct", 4): 4,
        ("add_ctct", 1): 1, ("add_ctct", 2): 2,  ("add_ctct", 3): 3, ("add_ctct", 4): 4,
        ("add_ctpt", 1): 1, ("add_ctpt", 2): 2,  ("add_ctpt", 3): 3, ("add_ctpt", 4): 4,
        ("sub_ctct", 1): 1, ("sub_ctct", 2): 2, ("sub_ctct", 3): 3, ("sub_ctct", 4): 4,
        ("sub_ctpt", 1): 1, ("sub_ctpt", 2): 2, ("sub_ctpt", 3): 3, ("sub_ctpt", 4): 4,
        ("bootstrap", 1): 10, ("bootstrap", 2): 10, ("bootstrap", 3): 10, ("bootstrap", 4): 10,
        }
    md = MultDepth()
    rt = Runtime(md, runtime_table)
    analyzer = Analyzer([md, rt])
    fun(analyzer)
    print(f"Total Runtime: {rt.total_runtime}")
    rt.anotate_metric()

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
    v2 = crypto_context.EvalAdd(v, v)
    v3 = crypto_context.EvalSub(v, v2)
    v4 = crypto_context.EvalMult(v, ciphertext1) 
    v6 = square(crypto_context, v)
    v7 = square(crypto_context, v6)