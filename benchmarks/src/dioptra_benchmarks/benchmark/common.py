# Class for displaying runtime of a chunk of code
# To be used with python's `with` syntax
import pathlib
import re
import subprocess
import sys
import time
import dioptra.utils.measurement

class DisplayTime:
    def __init__(self, p: str, display: bool = True):
        self.display = display
        self.p = p

    def __enter__(self):
        self.start = time.time_ns()
        return self

    def __exit__(self, *arg):
        end = time.time_ns()
        if self.display:
            print(f"{self.p}: {dioptra.utils.measurement.format_ns_approx(end - self.start)}")


mem_pattern = re.compile("^Max memory used: ([0-9]+)K", flags=re.MULTILINE)

def with_mem_usage(cmd):
  return  f"/usr/bin/time -f \"Max memory used: %MK\" {cmd}"

def rewrite_memory(blob: str) -> str:
  match = mem_pattern.search(blob)
  if match is not None:
    bytes = int(match.group(1)) * 1000
    fmtted = dioptra.utils.measurement.format_bytes(bytes)
    return mem_pattern.sub(f"Max memory used: {fmtted}", blob)

  return blob

