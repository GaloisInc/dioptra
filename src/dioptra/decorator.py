import datetime
import importlib.util
import inspect
from plistlib import InvalidFileException
import runpy
import sys
from typing import Callable

import dioptra.analyzer.binfhe.calibration as bin_cal
from dioptra.analyzer.calibration import Calibration, CalibrationData
from dioptra.analyzer.metrics.analysisbase import Analyzer
from dioptra.analyzer.metrics.multdepth import MultDepth
from dioptra.analyzer.metrics.runtime import Runtime
from dioptra.analyzer.utils.util import format_ns

pke_context_functions = []
bin_context_functions = []
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
  calibration = CalibrationData.read_json(sample_file)

  load_files(files)

  for (limit, desc, f) in runtime_functions:
    runtime_analysis = Runtime(calibration)
    analyzer = Analyzer([runtime_analysis], calibration.get_scheme())
    
    f(analyzer)

    if limit is None:
      status = "[-------]"

    elif runtime_analysis.total_runtime <= timedelta_as_ns(limit):
      status = "[OK     ]"

    else:
      status = "[TIMEOUT]"

    print(f"{status} {desc} ... { format_ns(runtime_analysis.total_runtime) }")

def annotate_main(sample_file: str, file: str, test_case: str, output: str) -> None:
  samples = CalibrationData.read_json(sample_file)

  runtime_analysis = Runtime(samples)
  analyzer = Analyzer([runtime_analysis], samples.scheme)

  load_files([file])

  for (_, desc, f) in runtime_functions:
    if desc == test_case:
      f(analyzer)
      runtime_analysis.anotate_metric()
      return 

def dioptra_context(description: str | None = None):
  def decorator(f):
    d = f.__name__ if description is None else description
    pke_context_functions.append((d, f))
    return f
  
  return decorator

def dioptra_binfhe_context(description: str | None = None):
  def decorator(f):
    d = f.__name__ if description is None else description
    bin_context_functions.append((d, f))
    return f
  
  return decorator

def context_list_main(files: list[str]):
  load_files(files)

  for (n, f) in pke_context_functions:
    file = inspect.getfile(f)
    (_, line) = inspect.getsourcelines(f)
    print(f"{n} (defined at {file}:{line})")

  for (n, f) in bin_context_functions:
    file = inspect.getfile(f)
    (_, line) = inspect.getsourcelines(f)
    print(f"{n} (defined at {file}:{line})")

def context_calibrate_main(files: list[str], name: str, outfile: str, samples: int = 5, quiet: bool = False):
  load_files(files)

  ctx_f = None
  is_pke = True
  # TODO: throw if context has name collision
  for (n, f) in pke_context_functions:
    if n == name:
      ctx_f = f

  for (n, f) in bin_context_functions:
    if n == name:
      is_pke = False
      ctx_f = f

  if ctx_f is None:
    print(f"Calibration failed: no context named '{name}' found", file=sys.stderr)
    sys.exit(-1)

  if is_pke:
    (cc, params, key_pair, features) = ctx_f()

    log = None if quiet else sys.stdout
    calibration = Calibration(cc, params, key_pair, features, log, sample_count=samples)
    smp = calibration.calibrate()
    smp.write_json(outfile)

  else:
    (cc, sk) = ctx_f()
    log = None if quiet else sys.stdout
    calibration = bin_cal.Calibration(cc, sk, log=log, sample_count=samples)
    cd = calibration.run()
    cd.write_json(outfile)


