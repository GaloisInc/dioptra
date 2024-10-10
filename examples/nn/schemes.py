import openfhe as ofhe

from time import time_ns
from random import random
from functools import reduce
from typing import Self

from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns
from dioptra.decorator import dioptra_runtime

class Scheme: 
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        raise NotImplementedError("Plaintext packing is not implemented for this scheme")
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        raise NotImplementedError("The zero value is not implemented for this scheme")
    def bootstrap(self, cc: ofhe.CryptoContext, level: int, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        pass

class CKKS(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakeCKKSPackedPlaintext([0.0])
    def bootstrap(self, cc: ofhe.CryptoContext,  level: int, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        if level % 10 == 0:
            return cc.EvalBootstrap(value)        
        else:
            return value

class BFV(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
       return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext,  level: int, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return value

class BGV(Scheme):
    def make_plaintext(self, cc: ofhe.CryptoContext, value: list[int]) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext(value)
    def zero(self, cc: ofhe.CryptoContext) -> ofhe.Plaintext:
        return cc.MakePackedPlaintext([0])
    def bootstrap(self, cc: ofhe.CryptoContext,  level: int, value: ofhe.Ciphertext) -> ofhe.Ciphertext:
        return value