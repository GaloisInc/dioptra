from analysis_base import AnalysisBase, Ciphertext
import dis
from inspect import Traceback

class MultDepth(AnalysisBase):
    depth : dict[Ciphertext, int]
    max_depth : int
    where : list[tuple[int, str, dis.Positions]]

    def __init__(self) -> None:
        self.depth = {}
        self.max_depth = 0
        self.where = []

    def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Traceback) -> None:
        new_depth = max(self.depth_of(ct1), self.depth_of(ct2)) + 1
        self.set_depth(dest, new_depth, call_loc)


    def depth_of(self, ct: Ciphertext) -> int:
        if ct in self.depth:
            return self.depth[ct]
        
        return 0
    
    def set_depth(self, ct: Ciphertext, depth: int, call_loc: Traceback) -> None:
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