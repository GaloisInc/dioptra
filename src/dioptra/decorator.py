import datetime
import importlib.util
from plistlib import InvalidFileException
import runpy
from typing import Callable

from dioptra.analyzer.calibration import RuntimeSamples
from dioptra.analyzer.metrics.analysisbase import Analyzer
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.metrics.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns

runtime_functions = []
def dioptra_runtime(samples_file: str, limit: datetime.timedelta | None = None, description: str | None = None) -> Callable:  #TODO better type
  def decorator(f):
    d = f.__name__ if description is None else description
    runtime_functions.append((samples_file, limit, d, f))
    return f
  
  return decorator

def timedelta_as_ns(d: datetime.timedelta) -> int:
  return d.microseconds * (10 ** 3) + \
         d.seconds * (10 ** 9) + \
         d.days * 24 * 3600 * (10 ** 9)


def annotate(file: str, function: str, outdir: str):
  pass

def report_main(files: list[str]) -> None:
  for file in files:
    print(f"loading {file}")
    runpy.run_path(file)

  for (sample_file, limit, desc, f) in runtime_functions:
    depth_analysis = MultDepth()
    samples = RuntimeSamples()
    samples.read_json(sample_file)
    runtime_analysis = Runtime(depth_analysis, samples)
    analyzer = Analyzer([runtime_analysis])
    
    f(analyzer)

    if limit is None:
      status = "[-------]"

    elif runtime_analysis.total_runtime <= timedelta_as_ns(limit):
      status = "[OK     ]"

    else:
      status = "[TIMEOUT]"

    print(f"{status} {desc} ... { format_ns(runtime_analysis.total_runtime) }")

    


