#!/usr/bin/env python
from operator import sub
import os
import pathlib
import re
import sys
import subprocess
import argparse
from unittest import expectedFailure

from benchmark.common import rewrite_memory, with_mem_usage
import dioptra.utils.measurement

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
main_loc = loc.joinpath("main.py").absolute()
estimates = loc.joinpath("estimates.py")

def dioptra_estimate():
  cmd = f"dioptra estimate report -cd {calibration_loc.joinpath('binfhe_128.cd')} {estimates}"
  print(f"Running: {cmd}")
  sys.stdout.flush()
  subprocess.call(cmd, shell=True)
  sys.stdout.flush()
  print()


def dioptra_execute(op: str, int_size: int, list_size: int):
  print(f"Running main.py with {op} int size {int_size} and list size {list_size}")
  cmd = f"python {main_loc} -op {op} --intsize {int_size} --listsize {list_size}"
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

  for op in ["any_eq", "zip_lt"]:
    for int_sz in [8, 16, 32, 64]:
      for list_sz in [8, 16, 32]:
        print(f"-- op {op} - int size: {int_sz} - list size: {list_sz}  --")
        dioptra_execute(op, int_sz, list_sz)

  print()
  print()

def main():
  parser = argparse.ArgumentParser(description='Dioptra Perceptron Benchmarks')

  subparsers = parser.add_subparsers(dest="command", required=True)

  est_parser = subparsers.add_parser("estimate", help='Run estimates using Dioptra')
  exe_parser = subparsers.add_parser("execute", help='Run the benchmark in OpenFHE')
  exe_parser.add_argument("-is", "--intsize", required=True, type=int, help="Size of the integers in the list")
  exe_parser.add_argument("-ls", "--listsize", required=True, type=int, help="Size of the list of integers")
  exe_parser.add_argument("-op", "--op", required=True, help="Program choices: zip-less-than or at-least-one equality", choices=["zip_lt", "any_eq"])

  subparsers.add_parser("runall", help='Run and estimate all the benchmarks with defaults')
  args = parser.parse_args()

  if args.command == "execute":
    dioptra_execute(args.op, args.intsize, args.listsize)
  elif args.command == "estimate":
    dioptra_estimate()
  elif args.command == "runall":
    run_all_benchmarks()
  else:
    raise NotImplementedError

if __name__ == '__main__':
  main()
