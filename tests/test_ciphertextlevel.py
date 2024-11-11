from audioop import add
from typing import Iterator
from unittest import TestCase, TestSuite
from dioptra.analyzer.scheme import LevelInfo, PkeSchemeModels
from tests.test_contexts import ckks1
import openfhe


class TestCiphertextLevel_CKKS(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (cc, params, key, _) = ckks1()
        cls._cc = cc
        cls._key_pair = key
        cls._parameters = params

    def setUp(self) -> None:
        super().setUp()
        self.cts: dict[LevelInfo, openfhe.Ciphertext] = {}

    def cc(self):
        return TestCiphertextLevel_CKKS._cc

    def key_pair(self):
        return TestCiphertextLevel_CKKS._key_pair

    def params(self):
        return TestCiphertextLevel_CKKS._parameters

    def mkct(self, lv: LevelInfo) -> openfhe.Ciphertext:
        if lv in self.cts:
            return self.cts[lv]

        slots = PkeSchemeModels.CKKS.num_slots(self.cc())
        vec = [0] * slots

        pt = self.cc().MakeCKKSPackedPlaintext(
            vec, level=lv.level, scaleDeg=lv.noise_scale_deg
        )
        ct0 = self.cc().Encrypt(self.key_pair().publicKey, pt)
        return ct0

    def all_levels(self) -> Iterator[LevelInfo]:
        for level in range(0, self.params().GetMultiplicativeDepth()):
            for noise_scale_deg in [1, 2]:
                yield LevelInfo(level=level, noise_scale_deg=noise_scale_deg)

    def test_mul_level(self):
        seen: set[frozenset[LevelInfo]] = set()
        for ct1 in self.all_levels():
            for ct2 in self.all_levels():
                if frozenset([ct1, ct2]) in seen:
                    continue

                mlev = PkeSchemeModels.CKKS.mul_level(ct1, ct2)
                mult_result = self.cc().EvalMult(self.mkct(ct1), self.mkct(ct2))
                self.assertEqual(
                    mlev.level,
                    mult_result.GetLevel(),
                    f"mul incorrect l1: [{ct1}] l2: [{ct2}] est: [{mlev}] actual level: {mult_result.GetLevel()}",
                )

                alev = PkeSchemeModels.CKKS.add_level(ct1, ct2)
                add_result = self.cc().EvalAdd(self.mkct(ct1), self.mkct(ct2))
                self.assertEqual(
                    alev.level,
                    add_result.GetLevel(),
                    f"add incorrect l1: [{ct1}] l2: [{ct2}] est: [{alev}] actual level: {add_result.GetLevel()}",
                )

                amlev = PkeSchemeModels.CKKS.mul_level(alev, alev)
                add_sq_result = self.cc().EvalMult(add_result, add_result)
                self.assertEqual(
                    amlev.level,
                    add_sq_result.GetLevel(),
                    f"add incorrect l1: [{alev}] l2: [{alev}] est: [{amlev}] actual level: {add_sq_result.GetLevel()}",
                )

                seen.add(frozenset([ct1, ct2]))
