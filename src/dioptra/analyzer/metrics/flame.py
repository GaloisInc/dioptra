from typing import IO
from dioptra.analyzer.calibration import Event, RuntimeTable
from dioptra.analyzer.metrics.analysisbase import AnalysisBase, Ciphertext, Plaintext
from dioptra.analyzer.utils.code_loc import Frame, StackLocation

class FlameGraph:
    def __init__(self) -> None:
        self.events: list[tuple[StackLocation|None, Event]] = []
    
    def add(self, c: Frame | None, e: Event) -> None:
        if c is None:
          self.events.append((c, e))

    def write_folded_file(self, rt: RuntimeTable, out: IO[str]) -> None:
        for (stack_loc, evt) in self.events:
            #TODO handle loc
            if stack_loc is not None:
              loc_lst = [l.function for l in stack_loc.stack_from_bottom()]
              loc_lst.append(evt.kind.name)
              loc_str = ";".join(loc_lst)
              t = rt.get_runtime_ns(evt)
              print(f"{loc_str} {t}")

class Flame(AnalysisBase):
  def __init__(self):
      self.graph = FlameGraph()

  def trace_encode(self, dest: Plaintext, level: int, call_loc: Frame | None) -> None:
      pass    
  def trace_encode_ckks(self, dest: Plaintext, level: int, call_loc: Frame | None) -> None:
      pass    
  def trace_encrypt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None) -> None:
      pass    
  def trace_decrypt(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None) -> None:
      pass
  

  def trace_bootstrap(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None) -> None:
      pass
  def trace_mul_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None) -> None:
      pass
  def trace_add_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None) -> None:
      pass
  def trace_sub_ctct(self, dest: Ciphertext, ct1: Ciphertext, ct2: Ciphertext, call_loc: Frame | None) -> None:
      pass
  def trace_mul_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None) -> None:
      pass
  def trace_add_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None) -> None:
      pass
  def trace_sub_ctpt(self, dest: Ciphertext, ct: Ciphertext, pt: Plaintext, call_loc: Frame | None) -> None:
      pass