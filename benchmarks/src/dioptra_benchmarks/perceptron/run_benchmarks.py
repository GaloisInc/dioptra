import os
import pathlib
import re
import sys
import subprocess
import argparse

from benchmark.common import rewrite_memory, with_mem_usage
import dioptra.utils.measurement

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
main_loc = loc.joinpath("main.py").absolute()
estimates = loc.joinpath("estimates.py")

def dioptra_estimate():
  cmd = f"dioptra estimate report -cd {calibration_loc.joinpath('ckks_128.cd')} {estimates}"
  print("Running: {cmd}")
  sys.stdout.flush()
  subprocess.call(cmd, shell=True)
  sys.stdout.flush()
  print()


def dioptra_execute(sz: int):
  print(f"Running main.py with input size {sz}")
  cmd = f"python {main_loc} {sz}"
  cmd = with_mem_usage(cmd)
  print(f"Running: {cmd}")
  sys.stdout.flush()
  output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
  print(rewrite_memory(output))
  sys.stdout.flush()

def run_all_benchmarks():
  print("Estimates:")

  dioptra_estimate()

  print()
  print()

  print("Actual Runtime:")

  for sz in [10, 50, 100]:
    print("-- Input size {sz} --")
    dioptra_execute(sz)

  print()
  print()

def main():
  parser = argparse.ArgumentParser(description='Dioptra Perceptron Benchmarks')

  subparsers = parser.add_subparsers(dest="command", required=True)

  est_parser = subparsers.add_parser("estimate", help='Run estimates using Dioptra')
  exe_parser = subparsers.add_parser("execute", help='Run the benchmark in OpenFHE')
  exe_parser.add_argument('-s','--size', help='The input size of the perceptron', required=True, type=int)

  subparsers.add_parser("runall", help='Run and estimate all the benchmarks with defaults')
  args = parser.parse_args()

  if args.command == "execute":
    dioptra_execute(args.size)
  elif args.command == "estimate":
    dioptra_estimate()
  elif args.command == "runall":
    run_all_benchmarks()
  else:
    raise NotImplementedError

if __name__ == '__main__':
  main()
