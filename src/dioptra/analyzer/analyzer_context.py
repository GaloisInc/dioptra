# from openfhe import CryptoContext, Ciphertext

import traceback
import sys


class Value:
    value_id = 0

    @staticmethod
    def fresh_id():
        id = Value.value_id
        Value.value_id += 1

    def __init__(self, id: int):
        self.id = id

    def __hash__(self) -> int:
        return self.id.__hash__()


class PrivateKey(Value):
    @staticmethod
    def fresh():
        return PrivateKey(Value.fresh_id())

class Ciphertext(Value):
    @staticmethod
    def fresh():
        return Ciphertext(Value.fresh_id())

class Plaintext(Value):
    @staticmethod
    def fresh():
        return Plaintext(Value.fresh_id())

class PublicKey(Value):
    @staticmethod
    def fresh():
        return PublicKey(Value.fresh_id())

class KeyPair:
    publicKey: PublicKey
    secretKey: PrivateKey

    def __init__(self, sk: PrivateKey, pk: PublicKey):
        self.publicKey = pk
        self.secretKey = sk


class OverloadResolution:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = dict(kwargs)  # maybe a bit of an oversimplification but...

    # simple fn with
    def resolve(self, *args, **kwargs):
        if len(self.args) != len(args):
            return False
        
        if len(self.kwargs) != len(kwargs):
            return False
        
        if not all([isinstance(self.args[x], args[x]) for x in range(0, len(args))]):
            return False
        
        # check that all specified args have the correct type
        for (name, ty) in kwargs:
            if not isinstance(self.kwargs[name], ty):
                return False
            
        # check that all kwargs are specified
        names = set([n for (n, _) in kwargs])
        return all([n in names for n in self.kwargs.keys()])
    

class AnalysisBase:
    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext):
        pass


class MultDepth(AnalysisBase):
    depth : dict[Ciphertext, int]
    max_depth : int
    where : list[traceback.StackSummary]

    def __init__(self):
        self.depth = {}
        self.max_depth = 0
        self.where = []

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext):
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth)


    def depth_of(self, ct: Ciphertext) -> int:
        if ct in self.depth:
            return self.depth[ct]
        
        return 0
    
    def set_depth(self, ct: Ciphertext, depth: int):
        if depth == 0:
            return

        self.depth[ct] = depth

        if depth == self.max_depth:
            self.where.append(traceback.extract_stack())

        elif depth > self.max_depth:
            self.max_depth = depth
            self.where = [traceback.extract_stack()]


class Analyzer:
    analysis_list : list[AnalysisBase]

    def __init__(self, analysis_list: list[AnalysisBase]):
        self.analysis_list = analysis_list

    def MakePackedPlaintext(self, value: list[int], noise_scale_deg: int = 1, level: int = 0) -> Plaintext:
        return Plaintext.fresh()

    def MakeCKKSPackedPlaintext(self, *args, **kwargs) -> Plaintext:
        resolver = OverloadResolution(args, kwargs)

        # TODO: params should be of type Openfhe.ParmType
        if resolver.resolve(list[float], scaleDeg = int, level = int, params = any, slots = int):
            return Plaintext.fresh()
    
    def KeyGen(self) -> KeyPair:
        return KeyPair(PrivateKey.fresh(), PublicKey.fresh())
    
    def EvalMultKeyGen(self, sk: PrivateKey) -> None:
        pass

    def EvalRotateKeyGen(self, sk: PrivateKey, index_list: list[int]) -> None:
        pass

    def Encrypt(self, public_key: PublicKey, plaintext: Plaintext) -> Ciphertext:
        return Ciphertext.fresh()
    
    def EvalMult(self, *args, **kwargs) -> Ciphertext:
        # resolver = OverloadResolution(args, kwargs)
        print(get_caller())
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            new = Ciphertext.fresh()
            for analysis in self.analysis_list:
                analysis.trace_mul_ctct(new, args[0], args[1])
            return new
        
        raise NotImplementedError("EvalMult: analyzer does not implement this overload")

call_loc = None
trace = True
def hello(frame, event, arg):
    print(frame)
    if trace and event == 'call':
        call_loc = frame

    return hello

def get_caller():
    trace = False
    print(call_loc)
    loc = call_loc.f_back.f_back
    trace = True
    return loc

def runexample():
    sys.settrace(hello)
    md = MultDepth()
    analyzer = Analyzer([md])
    example(analyzer)
    print(f"Max Depth: {md.max_depth}")
    newline = "\n"
    print(f"Location: {newline.join(md.where[0].format())}")

def example(crypto_context):
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
    v3 = crypto_context.EvalMult(v, v2)
    v4 = crypto_context.EvalMult(ciphertext1, ciphertext1)

# class AnalyzerContext:
#     def __init__(self, crypto_context):# type: ignore
#         self.crypto_context = crypto_context
        
#     def __getattr__(self, name):# type: ignore
#         try: 
#             getattr(self.crypto_context, name)
#         except AttributeError:
#             raise Exception(f"Attribute {name} is not implemented in OpenFHE")   
#         raise Exception(f"Attribute {name} is not implemented in Dioptra") 
    
#     def EvalAdd(*args, **kwargs):# type: ignore
#         print("EvalAdd!")
#     def EvalNegate(self: CryptoContext, ciphertext: Ciphertext):# type: ignore
#         print("EvalNegate!")

#     def EvalMult(*args, **kwargs):# type: ignore
#         print("EvalMult!")

#     def EvalBootstrap(self: CryptoContext, ciphertext: Ciphertext, numIterations: int = 1, precision: int = 0):# type: ignore
#         print("EvalBootstrap")

#     def EvalDivide(self: CryptoContext, ciphertext: Ciphertext, a: float, b: float, degree: int):# type: ignore
#         print("EvalDivide")

#     def EvalSub(*args, **kwargs):# type: ignore
#         print("EvalSub")

#     def EvalSum(self: CryptoContext, ciphertext: Ciphertext, batchSize: int):# type: ignore
#         print("EvalSum")