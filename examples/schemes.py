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
