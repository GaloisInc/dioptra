import os
import pathlib
import re
import sys
import subprocess

import dioptra.utils.measurement

mem_pattern = re.compile("^Max memory used: ([0-9]+)K", flags=re.MULTILINE)

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
pke_estimates = loc.joinpath("pke_estimates.py").absolute()
binfhe_estimates = loc.joinpath("binfhe_estimates.py").absolute()
main_loc = loc.joinpath("main.py").absolute()


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
    

def run_main(ctx_name: str, n: int):
  print(f"Running main.py with context {ctx_name} and matrix size {n}x{n}")
  cmd = f"python {main_loc} --dim1 {n}x{n} --dim2 {n}x1 --context {ctx_name} --no-setup-runtime"
  cmd = with_mem_usage(cmd)
  print(f"Running: {cmd}")
  sys.stdout.flush()
  output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
  print(rewrite_memory(output))
  print("-------------------------------")
  sys.stdout.flush()

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
    run_main(ctx, dim)

for ctx in ["ckks_128", "binfhe_128"]:
  for dim in [4, 16]:
    run_main(ctx, dim)
    
print()
print()

