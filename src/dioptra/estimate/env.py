from contextlib import contextmanager
import json
import pathlib
from typing import Any, Iterable
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.binfhe.calibration import BinFHECalibrationData
from dioptra.pke.calibration import PKECalibrationData
from dioptra.pke.analyzer import Analyzer
from dioptra.utils.file_loading import load_calibration_data
from dioptra.utils.scheme_type import SchemeType, calibration_type

class Environment:
  def __init__(self, name: str, calibration: PKECalibrationData | BinFHECalibrationData):
    self.name = name
    self.calibration: list[tuple[str, str, int]] = calibration

  def scheme_type(self) -> SchemeType:
    return calibration_type(self.calibration)

class EnvironmentsConfig:
  def __init__(self):
    self.envs: dict[str, Environment] = {}

  def get(self, name: str) -> Environment:
    env: Environment|None = self.envs.get(name)
    if env is None:
      raise ValueError(f"Environment '{name}' is not defined in environments config!")
    
    return env

  def load_from_file(self, file: pathlib.Path):
    basepath = file.parent
    with open(file) as f:
      obj = json.load(f)
      self.load(obj, basepath)

  def load(self, obj: Any, base_path: pathlib.Path):
    for env in obj["environments"]:
      name = env["name"]
      cal_file = base_path / pathlib.Path(env["calibration"])
      calibration = load_calibration_data(str(cal_file))
      if name in self.envs:
        raise ValueError("Duplicate name in environment config")
      
      self.envs[name] = Environment(name, calibration)

class Environments:
  @contextmanager
  def get_pke_ctx(self, name: str, phase: str | None = None) -> Iterable[Analyzer]:
    raise NotImplementedError()
  
  @contextmanager
  def get_bin_ctx(self, name: str, phase: str | None = None) -> Iterable[BinFHEAnalyzer]:
    raise NotImplementedError()
  

    