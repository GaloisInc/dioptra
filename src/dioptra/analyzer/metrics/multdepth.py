from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext, Plaintext, PublicKey, PrivateKey
import dis
from inspect import Traceback

class MultDepth(AnalysisBase):
    depth : dict[Ciphertext, int]
    max_depth : int
    where : dict[int, tuple[int, str, dis.Positions]]
    unit: str
    instruction_num: int

    def __init__(self) -> None:
        self.depth = {}
        self.max_depth = 0
        self.where = {}
        self.unit = ""

    def trace_encode(self, dest: Plaintext, level: int, call_loc: Traceback) -> None:
        new_depth = level
        self.set_depth(dest, new_depth, call_loc)   

    def trace_encode_ckks(self, dest: Plaintext, value: list[float], call_loc: Traceback, level: int = 0) -> None:
        new_depth = level
        self.set_depth(dest, new_depth, call_loc) 

    def trace_encrypt(self, dest: Ciphertext, publicKey: PublicKey, plaintext: Plaintext, call_loc: Traceback) -> None:
        new_depth = plaintext.level
        self.set_depth(dest, new_depth, call_loc)    

    def trace_decrypt(self, dest: Plaintext, publicKey: PublicKey, ciphertext: Ciphertext, call_loc: Traceback) -> None:
        new_depth = self.depth[ciphertext]
        self.set_depth(dest, new_depth, call_loc)    
    
    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth, call_loc)    

    def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        self.set_depth(dest, self.max_depth, call_loc)

    def trace_bootstrap(self, dest: Ciphertext, ct1: Ciphertext, call_loc: Traceback | None) -> None:
        new_depth = 0
        self.set_depth(dest, new_depth, call_loc)
    
    def depth_of(self, ct: Ciphertext) -> int:
        if ct in self.depth:
            return self.depth[ct]   
        return 0
    
    def set_depth(self, msg: Ciphertext | Plaintext, depth: int, call_loc: Traceback) -> None:
        self.depth[msg] = depth
        self.where[msg] = (depth, call_loc.filename, call_loc.positions) # type: ignore
        self.max_depth = max(depth, self.max_depth)