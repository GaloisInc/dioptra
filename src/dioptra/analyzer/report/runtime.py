from typing import Iterable
from dioptra.analyzer.utils.code_loc import Frame, SourceLocation, StackLocation

class RuntimeReport:
  def runtime_estimate(self, frame: Frame | None, ns: int):
    pass

class RuntimeTotal(RuntimeReport):
  def __init__(self):
    self.total_runtime = 0

  def runtime_estimate(self, frame: Frame | None, ns: int):
    self.total_runtime += ns

class RuntimeAnnotation(RuntimeReport):
  def __init__(self):
    self.runtimes: dict[str, dict[int, int]] = {}
    self.unaccounted_time = 0

  def runtime_estimate(self, frame: Frame | None, ns: int):
    loc = frame.source_location() if frame is not None else SourceLocation.unknown()
    if loc == SourceLocation.unknown() or loc.position.lineno is None:
      self.unaccounted_time += ns
      return

    if loc.filename not in self.runtimes:
      self.runtimes[loc.filename] = {}

    file_dict = self.runtimes[loc.filename]
    if loc.position.lineno not in file_dict:
      file_dict[loc.position.lineno] = 0

    file_dict[loc.position.lineno] += ns

  def annotation_dicts(self) -> Iterable[tuple[str, dict[int, int]]]:
    for n,v in self.runtimes.items():
      yield (n, v)

  def annotation_for(self, file: str) -> dict[int, int]:
    return self.runtimes.get(file, {})

class RuntimeLocSummary(RuntimeReport):
  def __init__(self):
    self.runtimes: dict[SourceLocation, int] = {}

  def runtime_estimate(self, frame: Frame | None, ns: int):
    loc = frame.source_location() if frame is not None else SourceLocation.unknown()
    cur = self.runtimes.get(loc, 0)
    self.runtimes[loc] = cur + ns


class RuntimeFlameGraph(RuntimeReport):
  def __init__(self):
    self.flame_graph: list[tuple[list[StackLocation], int]] = []

  def runtime_estimate(self, frame: Frame | None, ns: int):
    loc = frame.stack_location() if frame is not None else []
    self.flame_graph.append((loc, ns))