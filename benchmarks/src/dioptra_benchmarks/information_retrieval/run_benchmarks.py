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
import contexts
import dioptra.utils.measurement

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
main_loc = loc.joinpath("main.py").absolute()
pke_estimates = loc.joinpath("pke_estimates.py")
binfhe_estimates = loc.joinpath("binfhe_estimates.py")

def dioptra_estimate(ctx: str):
  estimates = pke_estimates if not contexts.is_binfhe(ctx) else binfhe_estimates
  cmd = f"dioptra estimate report -cd {calibration_loc.joinpath(ctx + ".cd")} {estimates}"
  print(f"Running: {cmd}")
  sys.stdout.flush()
  subprocess.call(cmd, shell=True)
  sys.stdout.flush()
  print()


def dioptra_execute(context: str, benchmark: str, db_size: int | None):
  print(f"Running main.py with {benchmark}")
  size_arg = "" if db_size is None else f"--database-size {db_size} "
  cmd = f"python {main_loc} --no-setup-runtime --context {context} {benchmark} {size_arg}"
  cmd = with_mem_usage(cmd)
  print(f"Running: {cmd}")
  sys.stdout.flush()
  output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
  print(rewrite_memory(output))
  sys.stdout.flush()

def run_all_benchmarks(ctx: str):
  print(f"----- Context: {ctx} ---------")
  print("Estimates:")

  dioptra_estimate(ctx)

  print()
  print()

  print("Actual Runtime:")
  
  if not contexts.is_binfhe(contexts):
    dioptra_execute(ctx, "private_weighting")

  for sz in [16,64,256,1024]:
    dioptra_execute(ctx, "retrieve", db_size=sz)

  print()
  print()
  print(f"------------------------------")
  print()
  print()

def main():
  parser = argparse.ArgumentParser(description='Dioptra PIR Benchmarks')

  allowed_contexts = ", ".join(sorted(contexts.contexts.keys()))

  parser.add_argument("--context", help="Context to use to do the computation (leave empty for all contexts)")
  subparsers = parser.add_subparsers(dest="command", required=True)
  est_parser = subparsers.add_parser("estimate", help='Run estimates using Dioptra')
  exe_parser = subparsers.add_parser("execute", help='Run the benchmark in OpenFHE')

  benchmarks = exe_parser.add_subparsers(description="benchmark", dest="benchmark", required=True)
  private_weighting = benchmarks.add_parser("private_weighting")
  retrieve = benchmarks.add_parser("retrieve", description="PIR retrieval benchmark")
  retrieve.add_argument("--database-size", type=int, required=True)

  subparsers.add_parser("runall", help='Run and estimate all the benchmarks with defaults')
  args = parser.parse_args()

  for ctx in contexts.contexts:
    if args.context is not None and ctx != args.context:
      continue

    if args.command == "execute":
      dioptra_execute(ctx, args.benchmark, args.database_size)
    elif args.command == "estimate":
      dioptra_estimate(ctx)
    elif args.command == "runall":
      run_all_benchmarks(ctx)
    else:
      raise NotImplementedError

if __name__ == '__main__':
  main()
