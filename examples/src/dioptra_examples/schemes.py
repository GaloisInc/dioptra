"""Scheme-agnostic OpenFHE interfaces.

This simplifies experimentation / examples that can be implemented using a
variety of FHE schemes, effectively providing an adapter for OpenFHE operations
that have different names depending on the scheme.
"""

import openfhe as ofhe


class Scheme:
    @staticmethod
    def make_plaintext(cc: ofhe.CryptoContext, value: list) -> ofhe.Plaintext:
        raise NotImplementedError(
            "Plaintext packing is not implemented for this scheme"
        )

    @staticmethod
    def zero(cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        raise NotImplementedError("The zero value is not implemented for this scheme")

    @staticmethod
    def bootstrap(cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        pass


class BFV(Scheme):
    @staticmethod
    def make_plaintext(cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)

    @staticmethod
    def zero(cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])

    @staticmethod
    def bootstrap(cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return value


class BGV(Scheme):
    @staticmethod
    def make_plaintext(cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)

    @staticmethod
    def zero(cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])

    @staticmethod
    def bootstrap(cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return value


class CKKS(Scheme):
    @staticmethod
    def make_plaintext(cc: ofhe.CryptoContext, value: list[float]) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext(value)

    @staticmethod
    def zero(cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext([0.0])

    @staticmethod
    def bootstrap(cc: ofhe.CryptoContext, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return cc.EvalBootstrap(value)
