
from typing import Callable
from dioptra.analyzer.utils import code_loc
from dioptra.analyzer.utils.code_loc import Frame
import dis
import os.path

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
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Value):
            return self.id == value.id
        return False


class PrivateKey(Value):
    pass

class Ciphertext(Value):
    pass

class Plaintext(Value):
    def __init__(self, level = 0):
        self.level = level
        super().__init__()

class PublicKey(Value):
    pass

class KeyPair:
    publicKey: PublicKey
    secretKey: PrivateKey

    def __init__(self, sk: PrivateKey, pk: PublicKey):
        self.publicKey = pk
        self.secretKey = sk
    

class AnalysisBase:
    where : dict[int | dis.Positions, tuple[int, str, str, dis.Positions]]
    def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame| None) -> None:
        pass    
    def trace_encode_ckks(self, dest: Plaintext, level: int, call_loc: Frame| None) -> None:
        pass    
    def trace_encrypt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame| None) -> None:
        pass    
    def trace_decrypt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame| None) -> None:
        pass
    def trace_bootstrap(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame| None) -> None:
        pass
    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame| None) -> None:
        pass
    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame| None) -> None:
        pass
    def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame| None) -> None:
        pass
    def trace_mul_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame| None) -> None:
        pass
    def trace_add_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame| None) -> None:
        pass
    def trace_sub_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame| None) -> None:
        pass
    def anotate_metric(self) -> None:
        anotated_files: dict[str, list[str]] = dict()
        for metrics in self.where.values():
            (_value, value_formated, file_name, position) = metrics
            if os.path.exists(file_name):
                lines = []
                if file_name in anotated_files.keys():
                    lines = anotated_files[file_name]
                else:
                    with open(file_name, "r") as file:
                        lines = file.readlines()
                lines[position.lineno - 1] = lines[position.lineno - 1].replace("\n", "") + " # "+type(self).__name__ +": " + str(value_formated) + "\n"
                anotated_files[file_name] = lines

        for file_name in anotated_files.keys():
            anotated_files[file_name] = lines
            file_name_anotated = file_name.replace(".py", "") + "_anotated.py"
            with open(file_name_anotated, 'w') as file_edited:
                file_edited.writelines(lines)


class Analyzer:
    analysis_list : list[AnalysisBase]

    def __init__(self, analysis_list: list[AnalysisBase]):
        self.analysis_list = analysis_list

    def KeyGen(self) -> KeyPair:
        return KeyPair(PrivateKey(), PublicKey())
    
    def EvalMultKeyGen(self, sk: PrivateKey) -> None:
        pass

    def EvalRotateKeyGen(self, sk: PrivateKey, index_list: list[int]) -> None:
        pass

    def MakePackedPlaintext(self, value: list[int], noise_scale_deg: int = 1, level: int = 0) -> Plaintext:
        new = Plaintext(level)
        caller_loc = code_loc.calling_frame()
        for analysis in self.analysis_list:
            analysis.trace_encode(new, level, caller_loc)
        return new

    def MakeCKKSPackedPlaintext(self, *args, **kwargs) -> Plaintext:#type: ignore
        level = kwargs.get('level',0)
        new = Plaintext(level)
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], list):
            for analysis in self.analysis_list:
                analysis.trace_encode_ckks(new, args[0], caller_loc, level)
            return new
        raise NotImplementedError("MakeCKKSPackedPlaintext: analyzer does not implement this overload")
    
    def Encrypt(self, public_key: PublicKey, plaintext: Plaintext) -> Ciphertext:
        new = Ciphertext()
        caller_loc = code_loc.calling_frame()
        for analysis in self.analysis_list:
            analysis.trace_encrypt(new, public_key, plaintext, caller_loc)
        return new
        
    def Decrypt(self, *args, **kwargs):
        new = Ciphertext()
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], PublicKey) and isinstance(args[1], Ciphertext):
            for analysis in self.analysis_list:
                analysis.trace_decrypt(new, args[0], args[1], caller_loc)
            return new
        raise NotImplementedError("Decrypt: analyzer does not implement this overload")
    
    def EvalMult(self, *args, **kwargs) -> Ciphertext:#type: ignore
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_mul_ctct(new, args[0], args[1], caller_loc)
            return new
        elif isinstance(args[0], Ciphertext) and isinstance(args[1], Plaintext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_mul_ctpt(new, args[0], args[1], caller_loc)
            return new
        raise NotImplementedError("EvalMult: analyzer does not implement this overload")
    
    def EvalAdd(self, *args, **kwargs) -> Ciphertext:#type: ignore
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_add_ctct(new, args[0], args[1], caller_loc)
            return new
        elif isinstance(args[0], Ciphertext) and isinstance(args[1], Plaintext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_add_ctpt(new, args[0], args[1], caller_loc)
            return new
        raise NotImplementedError("EvalAdd: analyzer does not implement this overload")
    
    def EvalSub(self, *args, **kwargs) -> Ciphertext:#type: ignore
        caller_loc = code_loc.calling_frame()
        if isinstance(args[0], Ciphertext) and isinstance(args[1], Ciphertext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_sub_ctct(new, args[0], args[1], caller_loc)
            return new
        elif isinstance(args[0], Ciphertext) and isinstance(args[1], Plaintext):
            new = Ciphertext()
            for analysis in self.analysis_list:
                analysis.trace_sub_ctpt(new, args[0], args[1], caller_loc)
            return new
        raise NotImplementedError("EvalSub: analyzer does not implement this overload")
    
    def EvalBootstrap(self, ciphertext: Ciphertext, _numIterations: int = 1, _precision: int = 0) -> Ciphertext: 
        caller_loc = code_loc.calling_frame()
        new = Ciphertext()
        for analysis in self.analysis_list:
            analysis.trace_bootstrap(new, ciphertext, caller_loc)
        return new
    
    def ArbitraryCT(self, level=0) -> Ciphertext:
        #TODO: incorporate level into this somehow
        return Ciphertext()
    
    def Analyze(self, f: Callable, *args, **kwargs):
        f(self, args, kwargs)

    # def _enable_trace(self):
    #     sys.settrace(self._trace)

    # def _trace(self, frame: any, event: str, arg: any) -> function:
    #     if event == 'call':
    #         caller = frame.f_back
    #         print(f"calling {frame.f_code.co_qualname} at {frame_loc(caller)}")

    #     if event == 'return' and frame.f_back is not None:
    #         caller = frame.f_back
    #         print(f"return from {frame.f_code.co_qualname} to {caller.f_code.co_qualname} at {frame_loc(caller)}")
    #     return self._trace