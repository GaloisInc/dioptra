import inspect
import dioptra.analyzer.utils.code_loc as code_loc
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
    where : dict[int, tuple[int, str, dis.Positions]]
    unit: str
    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: inspect.Traceback | None) -> None:
        pass
    def anotate_metric(self) -> None:
        anotated_files: dict[str, list[str]] = dict()
        for metrics in self.where.values():
            (value, file_name, position) = metrics
            lines = []
            if file_name in anotated_files.keys():
                lines = anotated_files[file_name]
            else:
                with open(file_name, "r") as file:
                    lines = file.readlines()
            lines[position.lineno - 1] = lines[position.lineno - 1].replace("\n", "") + " # "+type(self).__name__ +": " + str(value) + " " + self.unit + "\n"
            anotated_files[file_name] = lines
            file_name_anotated = file_name.replace(".py", "") + "_anotated.py"
            with open(file_name_anotated, 'w') as file_edited:
                file_edited.writelines(lines)

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