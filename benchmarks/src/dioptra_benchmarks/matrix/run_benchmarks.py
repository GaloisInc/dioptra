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
main_loc = loc.joinpath("main.py").absolute()

def pke_estimates(mode: str) -> pathlib.Path:
  if mode == "matrix":
    return loc.joinpath("pke_matrixmatrix_estimates.py").absolute()
  elif mode == "vector":
    return loc.joinpath("pke_matrixvector_estimates.py").absolute()
  else:
    raise ValueError(f"Mode {mode} does not exist")

def binfhe_estimates(mode: str) -> pathlib.Path:
  if mode == "matrix":
    return loc.joinpath("binfhe_matrixmatrix_estimates.py").absolute()
  elif mode == "vector":
    return loc.joinpath("binfhe_matrixvector_estimates.py").absolute()
  else:
    raise ValueError(f"Mode {mode} does not exist")

contexts = [("bfv_128", pke_estimates)
           ,("bgv_128", pke_estimates)
           ,("ckks_128", pke_estimates)
           ,("binfhe_128", binfhe_estimates)]

context_choices = [x for (x, _) in contexts]

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


def dioptra_execute_strdims(ctx_name: str, dim1: str, dim2: str):
  print(f"Running main.py with context {ctx_name} and matrix sizes {dim1} and {dim2}")
  cmd = f"python {main_loc} --dim1 {dim1} --dim2 {dim2} --context {ctx_name} --no-setup-runtime"
  cmd = with_mem_usage(cmd)
  print(f"Running: {cmd}")
  sys.stdout.flush()
  output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
  print(rewrite_memory(output))
  print("-------------------------------")
  sys.stdout.flush()

def dioptra_execute(ctx_name: str, dims: tuple[tuple[int, int], tuple[int, int]]):
  ((r1, c1), (r2, c2)) = dims
  dim1 = f"{r1}x{c1}"
  dim2 = f"{r2}x{c2}"
  dioptra_execute_strdims(ctx_name, dim1, dim2)

def run_all_benchmarks(mode: str):
  print("Estimates:")

  for context, estimates in contexts:
    dioptra_estimate(context, estimates(mode))

  print()
  print()

  print("Actual Runtime:")

  if mode == "vector":
    def expand_vec(ns):
      return list(((n,n), (n,1)) for n in ns )

    run_schema = [
      ("bfv_128", expand_vec([4, 8, 16, 32, 64, 128, 256])),
      ("bgv_128", expand_vec([4, 8, 16, 32, 64, 128])),
      ("ckks_128", expand_vec([4, 8, 16, 32])),
      ("binfhe_128", expand_vec([4, 8, 16]))
    ]
  if mode == "matrix":
    def expand_mat(ns):
      return list(((y,x),(x,y)) for x in ns for y in ns if y <= x)
    run_schema = [
      ("bfv_128", expand_mat([4, 8, 16, 32, 64, 128])),
      ("bgv_128", expand_mat([4, 8, 16, 32, 64])),
      ("ckks_128", expand_mat([4, 8, 12, 16])),
      ("binfhe_128", expand_mat([2,4,6,8]))
    ]

  for (ctx, dims) in run_schema:
    for dim in dims:
      dioptra_execute(ctx, dim)

  print()
  print()

def main():
  parser = argparse.ArgumentParser(description='Dioptra Matrix Benchmarks')


  subparsers = parser.add_subparsers(dest="command", required=True)

  est_parser = subparsers.add_parser("estimate", help='Run estimates using Dioptra')
  est_parser.add_argument('-cd','--ctxt', help='The context name to use for the benchmark', choices=context_choices, required=True, type=str)
  est_parser.add_argument('-m', "--mode",  help='The choice of benchmark, i.e. matrix multiplication or matrix-vector multiplication', choices=["matrix", "vector"], required=True, type=str)

  exe_parser = subparsers.add_parser("execute", help='Run the benchmark in OpenFHE')
  exe_parser.add_argument('-d1','--dimension1', help='The dimensions of the first matrix to benchmark (ex. 5x4)', required=True, type=str)
  exe_parser.add_argument('-d2','--dimension2', help='The dimensions of the second matrix to benchmark (use an Nx1 matrix for vector multiplication)', required=True, type=str)
  exe_parser.add_argument('-cd','--ctxt', help='The context name to use for the benchmark', choices=context_choices, required=True, type=str)

  all_parser = subparsers.add_parser("runall", help='Run and estimate all the benchmarks with defaults')
  all_parser.add_argument('-m', "--mode",  help='The choice of benchmark, i.e. matrix multiplication or matrix-vector multiplication', choices=["matrix", "vector"], required=True, type=str)
  args = parser.parse_args()

  if args.command == "execute":
    dioptra_execute_strdims(args.ctxt, args.dimension1, args.dimension2)
  elif args.command == "estimate":
    dioptra_estimate(args.ctxt, dict(contexts)[args.ctxt](args.mode))
  elif args.command == "runall":
    run_all_benchmarks(args.mode)
  else:
    raise NotImplementedError

if __name__ == '__main__':
  main()
