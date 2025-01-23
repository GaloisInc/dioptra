import os
import pathlib
import re
import sys
import subprocess
import argparse

import dioptra.utils.measurement

mem_pattern = re.compile("^Max memory used: ([0-9]+)K", flags=re.MULTILINE)

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
pke_estimates = loc.joinpath("pke_estimates.py").absolute()
binfhe_estimates = loc.joinpath("binfhe_estimates.py").absolute()
main_loc = loc.joinpath("main.py").absolute()

context_choices = ["bfv_128", "bgv_128", "ckks_128", "binfhe_128"]

def dioptra_estimate(ctx_name: str, est_loc: pathlib.Path):
  print(f"-- estimates for {ctx_name} --")
  cmd = f"dioptra estimate report -cd \"{calibration_loc.joinpath(ctx_name + ".cd") }\" {est_loc}"
  print(f"Running: {cmd}")
  sys.stdout.flush()
  subprocess.call(cmd, shell=True)
  sys.stdout.flush()
  print("-------------------------------")
  print()


def with_mem_usage(cmd):
  return  f"/usr/bin/time -f \"Max memory used: %MK\" {cmd}"

def rewrite_memory(blob: str) -> str:
  match = mem_pattern.search(blob)
  if match is not None:
    bytes = int(match.group(1)) * 1000
    fmtted = dioptra.utils.measurement.format_bytes(bytes)
    return mem_pattern.sub(f"Max memory used: {fmtted}", blob)

  return blob


def dioptra_execute(ctx_name: str, n: int):
  print(f"Running main.py with context {ctx_name} and matrix size {n}x{n}")
  cmd = f"python {main_loc} --dim1 {n}x{n} --dim2 {n}x1 --context {ctx_name} --no-setup-runtime"
  cmd = with_mem_usage(cmd)
  print(f"Running: {cmd}")
  sys.stdout.flush()
  output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
  print(rewrite_memory(output))
  print("-------------------------------")
  sys.stdout.flush()

def run_all_benchmarks():
  print("Estimates:")

  dioptra_estimate("bfv_128", pke_estimates)
  dioptra_estimate("bgv_128", pke_estimates)
  dioptra_estimate("ckks_128", pke_estimates)
  dioptra_estimate("binfhe_128", binfhe_estimates)

  print()
  print()

  print("Actual Runtime:")

  for ctx in ["bfv_128", "bgv_128"]:
    for dim in [4, 16, 64]:
      dioptra_execute(ctx, dim)

  for ctx in ["ckks_128", "binfhe_128"]:
    for dim in [4, 16]:
      dioptra_execute(ctx, dim)

  print()
  print()

def main():
  parser = argparse.ArgumentParser(
                    prog='Dioptra Matrix x Vector Benchmarks',
                    description='Benchmarks for Multiplication of degree-256 polynomial matrix X vector')

  group_run = parser.add_mutually_exclusive_group(required=True)
  group_run.add_argument('-exe','--execute', help='Run the benchmark in OpenFHE', action='store_true')
  group_run.add_argument('-est','--estimate', help='Estimate the benchmark using Dioptra', action='store_true')
  group_run.add_argument('-all','--runall', help='Run and estimate all the benchmarks', action='store_true')

  parser.add_argument('-estloc','--estimateloc', help='The path of the functions to estimate', required='--estimate' in sys.argv, nargs='?', const=pke_estimates, type=str)
  parser.add_argument('-d','--dimension', help='The dimension of the matrix and vector to benchmark', required='--execute' in sys.argv, type=int)
  parser.add_argument('-cd','--ctxt', help='The context name to use for the benchmark', choices=context_choices, required=('--estimate' or '--execute') in sys.argv, type=str)

  args = parser.parse_args()

  if args.execute:
    dioptra_execute(args.ctxt, args.dimension)
  elif args.estimate:
    dioptra_estimate(args.ctxt, args.estloc)
  elif args.runall:
    run_all_benchmarks()
  else:
    raise NotImplementedError

if __name__ == '__main__':
  main()
