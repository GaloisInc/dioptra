"""Scheme-agnostic OpenFHE interfaces.

This simplifies experimentation / examples that can be implemented using a
variety of FHE schemes, effectively providing an adapter for OpenFHE operations
that have different names depending on the scheme.
"""

import openfhe as ofhe


class Scheme:
    def make_plaintext(
        self, cc: ofhe.CryptoContext, value: list[int]
    ) -> ofhe.Plaintext:
        raise NotImplementedError(
            "Plaintext packing is not implemented for this scheme"
        )

    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        raise NotImplementedError("The zero value is not implemented for this scheme")

    def bootstrap(
        self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext
    ) -> ofhe.Ciphertext:
        pass


class BFV(Scheme):
    def make_plaintext(
        self, cc: ofhe.CryptoContext, value: list[int]
    ) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)

    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])

    def bootstrap(
        self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext
    ) -> ofhe.Ciphertext:
        return value


class BGV(Scheme):
    def make_plaintext(
        self, cc: ofhe.CryptoContext, value: list[int]
    ) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)

    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])

    def bootstrap(
        self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext
    ) -> ofhe.Ciphertext:
        return value


class CKKS(Scheme):
    def make_plaintext(
        self, cc: ofhe.CryptoContext, value: list[int]
    ) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext(value)

    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext([0.0])

    def bootstrap(
        self, cc: ofhe.CryptoContext, value: ofhe.Ciphertext
    ) -> ofhe.Ciphertext:
        return cc.EvalBootstrap(value)
