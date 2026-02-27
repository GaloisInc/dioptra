from contextlib import contextmanager
import pathlib
from typing import Iterable

from dioptra import binfhe, estimate
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.estimate.env import Environments, EnvironmentsConfig
from dioptra.pke.analyzer import Analyzer
from dioptra.pke.memory import PKEMemoryEstimate
from dioptra.pke.runtime import Runtime
from dioptra.report.memory import MemoryMaxReport
from dioptra.report.runtime import RuntimeTotal
from dioptra.utils.code_loc import TraceLoc
from dioptra.utils.file_loading import load_files
from dioptra.utils.measurement import format_ns_approx
from dioptra.utils.scheme_type import SchemeType

class EnvironmentsReport(Environments):
  def __init__(self, config: EnvironmentsConfig):
    self.config = config
    self.timeline = []

  @contextmanager
  def get_pke_ctx(self, name: str, phase: str | None = None) -> Iterable[Analyzer]:
    env = self.config.get(name)
    if(env.scheme_type() != SchemeType.PKE):
      raise ValueError(f"Environment '{env.name}' not a PKE environment - {env.scheme_type()}!")
    calibration = env.calibration
    
    maxmem = MemoryMaxReport()
    total = RuntimeTotal()
    runtime_analysis = Runtime(calibration, total)
    memory_analysis = PKEMemoryEstimate(
      calibration.setup_memory_size,
      calibration.ct_mem,
      calibration.pt_mem,
      maxmem,
    )

    with TraceLoc() as tloc:
      analyzer = Analyzer(
        [runtime_analysis, memory_analysis], calibration.get_scheme(), tloc
      )
      yield analyzer

    self.timeline.append((name, phase, total.total_runtime))

  
  @contextmanager
  def get_bin_ctx(self, name: str, phase: str | None = None) -> Iterable[BinFHEAnalyzer]:
    env = self.config.get(name)
    if(env.scheme_type() != SchemeType.BINFHE):
      raise ValueError(f"Environment '{env.name}' not a BinFHE environment!")
    calibration = env.calibration
    
    maxmem = MemoryMaxReport()
    total = RuntimeTotal()
    runtime_analysis = binfhe.runtime.RuntimeEstimate(calibration, total)
    memory_analysis = binfhe.memory.BinFHEMemoryEstimate(
      calibration.setup_memory_size,
      calibration.ct_mem,
      calibration.pt_mem,
      maxmem,
    )

    analysis = binfhe.memory.BinFHEAnalysisGroup([runtime_analysis, memory_analysis])

    with TraceLoc() as tloc:
      analyzer = BinFHEAnalyzer(
        calibration.params, analysis, tloc
      )
      yield analyzer

    self.timeline.append((name, phase, total.total_runtime))

def format_ns_timeline(ns: int) -> str:
    micro = ns // 1000
    milli = micro // 1000
    total_seconds = milli // 1000
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = (total_seconds) // 3600

    return f"{hours}h{minutes}m{seconds}s"

def timeline_main(env_file: pathlib.Path, files: list[pathlib.Path]):
  config = EnvironmentsConfig()
  config.load_from_file(env_file)
  load_files(files)

  for case in estimate.env_estimation_cases.values():
    envs = EnvironmentsReport(config)
    case.run(envs)

    print(case.description)
    total_time = sum(duration for (_, _, duration) in envs.timeline)
    for (env, phase, duration) in envs.timeline:
      percent_time = f"{100 * duration / total_time if total_time > 0 else 0:2f} %"
      print(f"{phase} [in {env}] Runtime: {format_ns_approx(duration)} ({percent_time})")

    print(f"Total time: {format_ns_approx(total_time)}")

