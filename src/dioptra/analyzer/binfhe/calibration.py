from typing import IO
import openfhe

from dioptra.analyzer.binfhe.event import Event

class CalibrationData:
  pass

def CalibrationEvent:
  def __init__()

class Calibration:
  def __init__(self, 
               cc: openfhe.BinFHEContext,
               sk: openfhe.LWEPrivateKey,
               iter: int = 5,
               log: IO | None = None):
    self.cc = cc
    self.sk = sk
    self.iter = iter
    self.log_out = log

  def log(self, s: str):
    if self.log_out is not None:
      print(s, file=self.log_out)

  def run(self) -> CalibrationData:
    for i in range(0, self.iter):
      def measure(e: Event)