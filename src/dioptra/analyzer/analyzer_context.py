import code_loc
import inspect
import dis

class Value:
    value_id = 0

    @staticmethod
    def fresh_id() -> int:
        id = Value.value_id
        Value.value_id += 1
        return id

    def __init__(self) -> None:
        self.id = Value.fresh_id()

    def __hash__(self) -> int:
        return self.id.__hash__()


class PrivateKey(Value):
    pass

class Ciphertext(Value):
    pass

class Plaintext(Value):
    pass

class PublicKey(Value):
    pass

class KeyPair:
    publicKey: PublicKey
    secretKey: PrivateKey

    def __init__(self, sk: PrivateKey, pk: PublicKey):
        self.publicKey = pk
        self.secretKey = sk
    

class AnalysisBase:
    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: inspect.Traceback) -> None:
        pass


class MultDepth(AnalysisBase):
    depth : dict[Ciphertext, int]
    max_depth : int
    where : list[tuple[int, str, dis.Positions]]

    def __init__(self) -> None:
        self.depth = {}
        self.max_depth = 0
        self.where = []

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: inspect.Traceback) -> None:
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth, call_loc)


    def depth_of(self, ct: Ciphertext) -> int:
        if ct in self.depth:
            return self.depth[ct]
        
        return 0
    
    def set_depth(self, ct: Ciphertext, depth: int, call_loc: inspect.Traceback) -> None:
        if depth == 0:
            return
        self.depth[ct] = depth

        self.where.append((depth, call_loc.filename, call_loc.positions)) # type: ignore
        print(self.where)
        self.max_depth = max(depth, self.max_depth)

    def anotate_depth(self) -> None:
        anotated_files: dict[str, list[str]] = dict()
        for mults in self.where:
            (depth, file_name, position) = mults
            lines = []
            if file_name in anotated_files.keys():
                lines = anotated_files[file_name]
            else:
                with open(file_name, "r") as file:
                    lines = file.readlines()
            lines[position.lineno - 1] = lines[position.lineno - 1].replace("\n", "") + " # Multiplicative Depth: " + str(depth) + "\n"
            anotated_files[file_name] = lines
            file_name_anotated = file_name.replace(".py", "") + "_anotated.py"
            with open(file_name_anotated, 'w') as file_edited:
                file_edited.writelines(lines)

class Runtime(AnalysisBase):
    total_runtime : int
    runtime_table : dict[str, int]

    def __init__(self, runtime_table: dict[str, int]) -> None:
        self.total_runtime = 0
        self.runtime_table = runtime_table

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, where: inspect.Traceback) -> None:
        self.total_runtime += self.runtime_table["mult_ctct"]
        pass
class Analyzer:
    analysis_list : list[AnalysisBase]

    def __init__(self, analysis_list: list[AnalysisBase]):
        self.analysis_list = analysis_list

    def MakePackedPlaintext(self, value: list[int], noise_scale_deg: int = 1, level: int = 0) -> Plaintext:
        return Plaintext()

    def MakeCKKSPackedPlaintext(self, *args, **kwargs) -> Plaintext:#type: ignore
        return Plaintext()
    
    def KeyGen(self) -> KeyPair:
        return KeyPair(PrivateKey(), PublicKey())
    
    def EvalMultKeyGen(self, sk: PrivateKey) -> None:
        pass

    def EvalRotateKeyGen(self, sk: PrivateKey, index_list: list[int]) -> None:
        pass

    def Encrypt(self, public_key: PublicKey, plaintext: Plaintext) -> Ciphertext:
        return Ciphertext()
    
    def EvalMult(self, *args, **kwargs) -> Ciphertext:#type: ignore
        # resolver = OverloadResolution(args, kwargs)
        # print(get_caller())
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_mul_ctct(new, args[0], args[1], caller_loc)
            return new
        
        raise NotImplementedError("EvalMult: analyzer does not implement this overload")

# call_loc = None
# trace = True
# def hello(frame, event, arg):
#     print(frame)
#     if trace and event == 'call':
#         call_loc = frame

#     return hello

# def get_caller():
#     trace = False
#     print(call_loc)
#     loc = call_loc.f_back.f_back
#     trace = True
#     return loc
