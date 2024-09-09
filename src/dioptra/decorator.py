import datetime
import importlib.util
import inspect
from plistlib import InvalidFileException
import runpy
import sys
from typing import Callable

from dioptra.analyzer.calibration import Calibration, CalibrationData
from dioptra.analyzer.metrics.analysisbase import Analyzer
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.metrics.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns

context_functions = []
runtime_functions = []

def dioptra_runtime(limit: datetime.timedelta | None = None, description: str | None = None) -> Callable:  #TODO better type
  def decorator(f):
    d = f.__name__ if description is None else description
    runtime_functions.append((limit, d, f))
    return f
  
  return decorator


def timedelta_as_ns(d: datetime.timedelta) -> int:
  return d.microseconds * (10 ** 3) + \
         d.seconds * (10 ** 9) + \
         d.days * 24 * 3600 * (10 ** 9)


def annotate(file: str, function: str, outdir: str):
  pass


def load_files(files: list[str]) -> None:
  for file in files:
    runpy.run_path(file)

def report_main(sample_file: str, files: list[str]) -> None:
  samples = CalibrationData()
  samples.read_json(sample_file)

  load_files(files)

  for (limit, desc, f) in runtime_functions:
    depth_analysis = MultDepth()
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

def annotate_main(sample_file: str, file: str, test_case: str, output: str) -> None:
  samples = CalibrationData()
  samples.read_json(sample_file)

  runtime_analysis = Runtime(samples)
  analyzer = Analyzer([runtime_analysis], samples.scheme)

  load_files(file)

  for (_, desc, f) in runtime_functions:
    if desc == test_case:
      f(analyzer)
      runtime_analysis.anotate_metric()
      return 


    

def dioptra_context(description: str | None = None):
  def decorator(f):
    d = f.__name__ if description is None else description
    context_functions.append((d, f))
    return f
  
  return decorator

def context_list_main(files: list[str]):
  load_files(files)

  for (n, f) in context_functions:
    file = inspect.getfile(f)
    (_, line) = inspect.getsourcelines(f)
    print(f"{n} (defined at {file}:{line})")

def context_calibrate_main(files: list[str], name: str, outfile: str, samples: int = 5, quiet: bool = False):
  load_files(files)

  ctx_f = None
  for (n, f) in context_functions:
    if n == name:
      ctx_f = f

  if ctx_f is None:
    print(f"Calibration failed: no context named '{name}' found", file=sys.stderr)
    sys.exit(-1)

  (cc, params, key_pair, features) = ctx_f()
  log = None if quiet else sys.stdout
  calibration = Calibration(cc, params, key_pair, features, log, sample_count=samples)
  smp = calibration.calibrate()
  smp.write_json(outfile)


