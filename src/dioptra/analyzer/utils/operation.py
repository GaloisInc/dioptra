# type: ignore
from dioptra.analyzer_context import (
    PublicKey,
    Plaintext,
    Ciphertext,
    PrivateKey,
    PublicKey,
)


# List of all operations in OpenFHE CryptoContext
class Operations:
    @staticmethod
    def ClearEvalAutomorphismKeys() -> None:
        pass

    @staticmethod
    def ClearEvalMultKeys() -> None:
        pass

    def Decrypt(*args, **kwargs):
        pass

    @staticmethod
    def DeserializeEvalAutomorphismKey(*args, **kwargs):
        pass

    @staticmethod
    def DeserializeEvalMultKey(*args, **kwargs):
        pass

    def Enable(self, feature: PKESchemeFeature) -> None:
        pass

    def Encrypt(self, publicKey: PublicKey, plaintext: Plaintext) -> Ciphertext:
        pass

    def EvalAdd(*args, **kwargs):
        pass

    def EvalAddInPlace(*args, **kwargs):
        pass

    def EvalAddManyInPlace(self, ciphertextVec: List[Ciphertext]) -> Ciphertext:
        pass

    def EvalAddMutable(*args, **kwargs):
        pass

    def EvalAddMutableInPlace(
        self, ciphertext1: Ciphertext, ciphertext2: Ciphertext
    ) -> None:
        pass

    def EvalAtIndex(self, ciphertext: Ciphertext, index: int) -> Ciphertext:
        pass

    def EvalAtIndexKeyGen(
        self, privateKey: PrivateKey, indexList: List[int], publicKey: PublicKey = None
    ) -> None:
        pass

    def EvalAutomorphismKeyGen(
        self, privateKey: PrivateKey, indexList: List[int]
    ) -> EvalKeyMap:
        pass

    def EvalBootstrap(
        self, ciphertext: Ciphertext, numIterations: int = 1, precision: int = 0
    ) -> Ciphertext:
        pass

    def EvalBootstrapKeyGen(self, privateKey: PrivateKey, slots: int) -> None:
        pass

    def EvalBootstrapSetup(
        self,
        levelBudget: List[int] = [5, 4],
        dim1: List[int] = [0, 0],
        slots: int = 0,
        correctionFactor: int = 0,
        precompute: bool = True,
    ) -> None:
        pass

    def EvalCKKStoFHEW(
        self, ciphertext: Ciphertext, numCtxts: int = 0
    ) -> List[LWECiphertext]:
        pass

    def EvalCKKStoFHEWKeyGen(self, keyPair: KeyPair, lwesk: LWEPrivateKey) -> None:
        pass

    def EvalCKKStoFHEWPrecompute(self, scale: float = 1.0) -> None:
        pass

    def EvalCKKStoFHEWSetup(self, schswchparams: SchSwchParams) -> LWEPrivateKey:
        pass

    def EvalChebyshevFunction(
        self,
        func: Callable[[float], float],
        ciphertext: Ciphertext,
        a: float,
        b: float,
        degree: int,
    ) -> Ciphertext:
        pass

    def EvalChebyshevSeries(
        self, ciphertext: Ciphertext, coefficients: List[float], a: float, b: float
    ) -> Ciphertext:
        pass

    def EvalChebyshevSeriesLinear(
        self, ciphertext: Ciphertext, coefficients: List[float], a: float, b: float
    ) -> Ciphertext:
        pass

    def EvalChebyshevSeriesPS(
        self, ciphertext: Ciphertext, coefficients: List[float], a: float, b: float
    ) -> Ciphertext:
        pass

    def EvalCompareSchemeSwitching(
        self,
        ciphertext1: Ciphertext,
        ciphertext2: Ciphertext,
        numCtxts: int = 0,
        numSlots: int = 0,
        pLWE: int = 0,
        scaleSign: float = 1.0,
        unit: bool = False,
    ) -> Ciphertext:
        pass

    def EvalCompareSwitchPrecompute(
        self, pLWE: int = 0, scaleSign: float = 1.0, unit: bool = False
    ) -> None:
        pass

    def EvalCos(
        self, ciphertext: Ciphertext, a: float, b: float, degree: int
    ) -> Ciphertext:
        pass

    def EvalDivide(
        self, ciphertext: Ciphertext, a: float, b: float, degree: int
    ) -> Ciphertext:
        pass

    def EvalFHEWtoCKKS(
        self,
        LWECiphertexts: List[LWECiphertext],
        numCtxts: int = 0,
        numSlots: int = 0,
        p: int = 4,
        pmin: float = 0.0,
        pmax: float = 2.0,
        dim1: int = 0,
    ) -> Ciphertext:
        pass

    def EvalFHEWtoCKKSKeyGen(
        self,
        keyPair: KeyPair,
        lwesk: LWEPrivateKey,
        numSlots: int = 0,
        numCtxts: int = 0,
        dim1: int = 0,
        L: int = 0,
    ) -> None:
        pass

    def EvalFHEWtoCKKSSetup(
        self, ccLWE: BinFHEContext, numSlotsCKKS: int = 0, logQ: int = 25
    ) -> None:
        pass

    def EvalFastRotation(
        self, ciphertext: Ciphertext, index: int, m: int, digits: Ciphertext
    ) -> Ciphertext:
        pass

    def EvalFastRotationExt(
        self, ciphertext: Ciphertext, index: int, digits: Ciphertext, addFirst: bool
    ) -> Ciphertext:
        pass

    def EvalFastRotationPrecompute(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def EvalInnerProduct(*args, **kwargs):
        pass

    def EvalLinearWSum(
        self, ciphertext: List[Ciphertext], coefficients: List[float]
    ) -> Ciphertext:
        pass

    def EvalLinearWSumMutable(
        self, ciphertext: List[float], coefficients: List[Ciphertext]
    ) -> Ciphertext:
        pass

    def EvalLogistic(
        self, ciphertext: Ciphertext, a: float, b: float, degree: int
    ) -> Ciphertext:
        pass

    def EvalMaxSchemeSwitching(
        self,
        ciphertext: Ciphertext,
        publicKey: PublicKey,
        numValues: int = 0,
        numSlots: int = 0,
        pLWE: int = 0,
        scaleSign: float = 1.0,
    ) -> List[Ciphertext]:
        pass

    def EvalMaxSchemeSwitchingAlt(
        self,
        ciphertext: Ciphertext,
        publicKey: PublicKey,
        numValues: int = 0,
        numSlots: int = 0,
        pLWE: int = 0,
        scaleSign: float = 1.0,
    ) -> List[Ciphertext]:
        pass

    def EvalMerge(self, ciphertextVec: List[Ciphertext]) -> Ciphertext:
        pass

    def EvalMinSchemeSwitching(
        self,
        ciphertext: Ciphertext,
        publicKey: PublicKey,
        numValues: int = 0,
        numSlots: int = 0,
        pLWE: int = 0,
        scaleSign: float = 1.0,
    ) -> List[Ciphertext]:
        pass

    def EvalMinSchemeSwitchingAlt(
        self,
        ciphertext: Ciphertext,
        publicKey: PublicKey,
        numValues: int = 0,
        numSlots: int = 0,
        pLWE: int = 0,
        scaleSign: float = 1.0,
    ) -> List[Ciphertext]:
        pass

    def EvalMult(*args, **kwargs):
        pass

    def EvalMultAndRelinearize(
        self, ciphertext1: Ciphertext, ciphertext2: Ciphertext
    ) -> Ciphertext:
        pass

    def EvalMultKeyGen(self, privateKey: PrivateKey) -> None:
        pass

    def EvalMultKeysGen(self, privateKey: PrivateKey) -> None:
        pass

    def EvalMultMany(self, ciphertextVec: List[Ciphertext]) -> Ciphertext:
        pass

    def EvalMultMutable(*args, **kwargs):
        pass

    def EvalMultMutableInPlace(
        self, ciphertext1: Ciphertext, ciphertext2: Ciphertext
    ) -> None:
        pass

    def EvalMultNoRelin(
        self, ciphertext1: Ciphertext, ciphertext2: Ciphertext
    ) -> Ciphertext:
        pass

    def EvalNegate(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def EvalNegateInPlace(self, ciphertext: Ciphertext) -> None:
        pass

    def EvalPoly(self, ciphertext: Ciphertext, coefficients: List[float]) -> Ciphertext:
        pass

    def EvalPolyLinear(
        self, ciphertext: Ciphertext, coefficients: List[float]
    ) -> Ciphertext:
        pass

    def EvalPolyPS(
        self, ciphertext: Ciphertext, coefficients: List[float]
    ) -> Ciphertext:
        pass

    def EvalRotate(self, ciphertext: Ciphertext, index: int) -> Ciphertext:
        pass

    def EvalRotateKeyGen(
        self, privateKey: PrivateKey, indexList: List[int], publicKey: PublicKey = None
    ) -> None:
        pass

    def EvalSchemeSwitchingKeyGen(self, keyPair: KeyPair, lwesk: LWEPrivateKey) -> None:
        pass

    def EvalSchemeSwitchingSetup(self, schswchparams: SchSwchParams) -> LWEPrivateKey:
        pass

    def EvalSin(
        self, ciphertext: Ciphertext, a: float, b: float, degree: int
    ) -> Ciphertext:
        pass

    def EvalSquare(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def EvalSquareInPlace(self, ciphertext: Ciphertext) -> None:
        pass

    def EvalSquareMutable(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def EvalSub(*args, **kwargs):
        pass

    def EvalSubInPlace(*args, **kwargs):
        pass

    def EvalSubMutable(*args, **kwargs):
        pass

    def EvalSubMutableInPlace(
        self, ciphertext1: Ciphertext, ciphertext2: Ciphertext
    ) -> None:
        pass

    def EvalSum(self, ciphertext: Ciphertext, batchSize: int) -> Ciphertext:
        pass

    def EvalSumCols(
        self, ciphertext: Ciphertext, rowSize: int, evalSumKeyMap: EvalKeyMap
    ) -> Ciphertext:
        pass

    def EvalSumColsKeyGen(
        self, privateKey: PrivateKey, publicKey: PublicKey = None
    ) -> EvalKeyMap:
        pass

    def EvalSumKeyGen(
        self, privateKey: PrivateKey, publicKey: PublicKey = None
    ) -> None:
        pass

    def EvalSumRows(
        self,
        ciphertext: Ciphertext,
        rowSize: int,
        evalSumKeyMap: EvalKeyMap,
        subringDim: int = 0,
    ) -> Ciphertext:
        pass

    def EvalSumRowsKeyGen(
        self,
        privateKey: PrivateKey,
        publicKey: PublicKey = None,
        rowSize: int = 0,
        subringDim: int = 0,
    ) -> EvalKeyMap:
        pass

    def FindAutomorphismIndex(self, idx: int) -> int:
        pass

    def FindAutomorphismIndices(self, idxList: List[int]) -> List[int]:
        pass

    def GetBinCCForSchemeSwitch(self) -> BinFHEContext:
        pass

    def GetCyclotomicOrder(self) -> int:
        pass

    def GetDigitSize(self) -> int:
        pass

    def GetEvalSumKeyMap(self, arg0: str) -> EvalKeyMap:
        pass

    def GetKeyGenLevel(self) -> int:
        pass

    def GetModulus(self) -> float:
        pass

    def GetModulusCKKS(self) -> int:
        pass

    def GetPlaintextModulus(self) -> int:
        pass

    def GetRingDimension(self) -> int:
        pass

    def GetScalingFactorReal(self, arg0: int) -> float:
        pass

    def GetScalingTechnique(self) -> ScalingTechnique:
        pass

    @staticmethod
    def InsertEvalMultKey(evalKeyVec: List[EvalKey]) -> None:
        pass

    @staticmethod
    def InsertEvalSumKey(evalKeyMap: EvalKeyMap, keyTag: str = "") -> None:
        pass

    def IntMPBootAdd(self, sharePairVec: List[List[Ciphertext]]) -> List[Ciphertext]:
        pass

    def IntMPBootAdjustScale(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def IntMPBootDecrypt(
        self, privateKey: PrivateKey, ciphertext: Ciphertext, a: Ciphertext
    ) -> List[Ciphertext]:
        pass

    def IntMPBootEncrypt(
        self,
        publicKey: PublicKey,
        sharePair: List[Ciphertext],
        a: Ciphertext,
        ciphertext: Ciphertext,
    ) -> Ciphertext:
        pass

    def IntMPBootRandomElementGen(self, publicKey: PublicKey) -> Ciphertext:
        pass

    def KeyGen(self) -> KeyPair:
        pass

    def KeySwitchGen(
        self, oldPrivateKey: PrivateKey, newPrivateKey: PrivateKey
    ) -> EvalKey:
        pass

    def MakeCKKSPackedPlaintext(*args, **kwargs):
        pass

    def MakeCoefPackedPlaintext(
        self, value: List[int], noiseScaleDeg: int = 1, level: int = 0
    ) -> Plaintext:
        pass

    def MakePackedPlaintext(
        self, value: List[int], noiseScaleDeg: int = 1, level: int = 0
    ) -> Plaintext:
        pass

    def MakeStringPlaintext(self, str: str) -> Plaintext:
        pass

    def ModReduce(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def ModReduceInPlace(self, ciphertext: Ciphertext) -> None:
        pass

    def MultiAddEvalKeys(
        self, evalKey1: EvalKey, evalKey2: EvalKey, keyId: str = ""
    ) -> EvalKey:
        pass

    def MultiAddEvalMultKeys(
        self, evalKey1: EvalKey, evalKey2: EvalKey, keyId: str = ""
    ) -> EvalKey:
        pass

    def MultiAddEvalSumKeys(
        self, evalKeyMap1: EvalKeyMap, evalKeyMap2: EvalKeyMap, keyId: str = ""
    ) -> EvalKeyMap:
        pass

    def MultiEvalSumKeyGen(
        self, privateKey: PrivateKey, evalKeyMap: EvalKeyMap, keyId: str = ""
    ) -> EvalKeyMap:
        pass

    def MultiKeySwitchGen(
        self,
        originalPrivateKey: PrivateKey,
        newPrivateKey: PrivateKey,
        evalKey: EvalKey,
    ) -> EvalKey:
        pass

    def MultiMultEvalKey(
        self, privateKey: PrivateKey, evalKey: EvalKey, keyId: str = ""
    ) -> EvalKey:
        pass

    def MultipartyDecryptFusion(self, ciphertextVec: List[Ciphertext]) -> Plaintext:
        pass

    def MultipartyDecryptLead(
        self, ciphertextVec: List[Ciphertext], privateKey: PrivateKey
    ) -> List[Ciphertext]:
        pass

    def MultipartyDecryptMain(
        self, ciphertextVec: List[Ciphertext], privateKey: PrivateKey
    ) -> List[Ciphertext]:
        pass

    def MultipartyKeyGen(*args, **kwargs):
        pass

    def ReEncrypt(
        self, ciphertext: Ciphertext, evalKey: EvalKey, publicKey: PublicKey = None
    ) -> Ciphertext:
        pass

    def ReKeyGen(self, oldPrivateKey: PrivateKey, newPublicKey: PublicKey) -> EvalKey:
        pass

    def Relinearize(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def RelinearizeInPlace(self, ciphertext: Ciphertext) -> None:
        pass

    def Rescale(self, ciphertext: Ciphertext) -> Ciphertext:
        pass

    def RescaleInPlace(self, ciphertext: Ciphertext) -> None:
        pass

    @staticmethod
    def SerializeEvalAutomorphismKey(*args, **kwargs):
        pass

    @staticmethod
    def SerializeEvalMultKey(*args, **kwargs):
        pass

    def SetKeyGenLevel(self, level: int) -> None:
        pass

    def get_ptr(self) -> None:
        pass
