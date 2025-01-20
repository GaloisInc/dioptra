
import argparse
import re
import sys
from typing import Any
from benchmarks.src.dioptra_benchmarks.matrix.matrix import MatrixBuilder
import contexts
import benchmark.common as common


def fail(msg: str) -> Any:
  print(msg, file=sys.stderr)
  sys.exit(-1)

dim_pat = re.compile("^([0-9]+)[xX]([0-9]+)$")

def decode_dim(dimstr: str) -> tuple[int, int]:
  match = dim_pat.match(dimstr)
  if match is None:
    return fail(f"Expecting dimension argument to be of the form NxM - ex: 5x4")

  return (int(match.group(1)), int(match.group(2)))

def main():
  allowed_contexts = ", ".join(sorted(contexts.contexts.keys()))
  parser = argparse.ArgumentParser(prog="matrixvector.py", description="matrix/vector multiplication example"
                                                         , epilog=f"allowed contexts: {allowed_contexts}")

  parser.add_argument("--dim1", required=True, help="Dimension of first matrix written as NxM where N and M are integers")
  parser.add_argument("--dim2", required=True, help="Dimension of first matrix written as NxM where N and M are integers")
  parser.add_argument("--context", required=True, help="Context to use to do the computation")
  parser.add_argument("--no-setup-runtime", default=False, action='store_true')

  config = parser.parse_args()
  if not config.context in contexts.contexts:
    print(f"Unknown context name: '{config.context}'", file=sys.stderr)


    print(f"Valid contexts are: { allowed_contexts }", file=sys.stderr)
    sys.exit(-1)

  (rows1, cols1) = decode_dim(config.dim1)
  (rows2, cols2) = decode_dim(config.dim2)

  with common.DisplayTime("setup", not config.no_setup_runtime) as _:
    (cinfo, mk_builder) = contexts.contexts[config.context]()
    if len(cinfo) == 4:
      (cc, _, kp, _) = cinfo
      enc_key = kp.publicKey

    elif len(cinfo) == 2:
      (cc, enc_key) = cinfo

    else:
      fail("[BUG] context function returned wrong number of elements")

    builder: MatrixBuilder = mk_builder(cc)

  with common.DisplayTime("encoding/encrypting matricies", not config.no_setup_runtime) as _:
    mat1 = builder.random_matrix(rows1, cols1, enc_key)
    mat2 = builder.random_matrix(rows2, cols2, enc_key)

  with common.DisplayTime("multiplication") as _:
    _ = mat1 * mat2

if __name__ == '__main__':
  main()