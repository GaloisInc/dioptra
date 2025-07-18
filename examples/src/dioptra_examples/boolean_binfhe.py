import openfhe as ofhe

from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.binfhe.value import LWECiphertext
from dioptra.estimate import dioptra_binfhe_estimation


def simple_circuit(cc: ofhe.CryptoContext, ct1: LWECiphertext, ct2: LWECiphertext):
    # Sample Program: Step 4: Evaluation

    # Compute (1 AND 1) = 1; Other binary gate options are OR, NAND, and NOR
    ctAND1 = cc.EvalBinGate(ofhe.AND, ct1, ct2)

    # Compute (NOT 1) = 0
    ct2Not = cc.EvalNOT(ct2)

    # Compute (1 AND (NOT 1)) = 0
    ctAND2 = cc.EvalBinGate(ofhe.AND, ct2Not, ct1)

    # Compute OR of the result in ctAND1 and ctAND2
    return cc.EvalBinGate(ofhe.OR, ctAND1, ctAND2)


@dioptra_binfhe_estimation()
def est_simple_circuit(cc: BinFHEAnalyzer):
    sk = cc.KeyGen()
    ct1 = cc.Encrypt(sk, 1)
    ct2 = cc.Encrypt(sk, 1)
    result_ct = simple_circuit(cc, ct1, ct2)
    result_plain = cc.Decrypt(sk, result_ct)
    assert result_plain == 1


def main():
    ## Sample Program: Step 1: Set CryptoContext

    cc = ofhe.BinFHEContext()

    """
    STD128 is the security level of 128 bits of security based on LWE Estimator
    and HE standard. Other common options are TOY, MEDIUM, STD192, and STD256.
    MEDIUM corresponds to the level of more than 100 bits for both quantum and
    classical computer attacks
    """
    cc.GenerateBinFHEContext(ofhe.STD128, ofhe.GINX)

    ## Sample Program: Step 2: Key Generation

    # Generate the secret key
    sk = cc.KeyGen()

    print("Generating the bootstrapping keys...\n")

    # Generate the bootstrapping keys (refresh and switching keys)
    cc.BTKeyGen(sk)

    # Sample Program: Step 3: Encryption
    """
    Encrypt two ciphertexts representing Boolean True (1).
    By default, freshly encrypted ciphertexts are bootstrapped.
    If you wish to get a fresh encryption without bootstrapping, write
    ct1 = cc.Encrypt(sk, 1, FRESH)
    """
    ct1 = cc.Encrypt(sk, 1)
    ct2 = cc.Encrypt(sk, 1)
    ctResult = simple_circuit(cc, ct1, ct2)
    result = cc.Decrypt(sk, ctResult)

    print(f"Result of encrypted computation of (1 AND 1) OR (1 AND (NOT 1)) = {result}")


if __name__ == "__main__":
    main()
