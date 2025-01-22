import argparse
import os

def relpath(path) -> str:
  return os.path.join(os.path.dirname(__file__), path)

ckks1_calibration = relpath("examples/ckks1.dc")

def dioptra_estimate_report(target_file, calibration_file):
  os.system(f"dioptra estimate report -cd {calibration_file} {target_file}")

def benchmark(cmdline: str) -> None:
  os.system(f"/usr/bin/time -f \"Total runtime: %E - Max memory used: %MK\" {cmdline}")

class PerceptronBenchmark:
  def estimate(self):
    dioptra_estimate_report()

  def run(self):
    run()

def main():
  pass