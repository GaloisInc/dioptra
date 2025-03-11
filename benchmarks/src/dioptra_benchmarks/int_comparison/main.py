
import argparse
import re
import sys
from typing import Any
import compare
import context
from benchmark.circuit import BinFHEEncoder, Circuit
import benchmark.common as common
import random as random


def fail(msg: str) -> Any:
  print(msg, file=sys.stderr)
  sys.exit(-1)

def make_random_int(insize: int) -> int:
    return random.randint(0, 2**insize)

def make_randomlist(insize: int, listsize: int):
    return [make_random_int(insize) for _ in range(listsize)]

def encrypt_list(enc: BinFHEEncoder, insize: int, input: list[int]) -> list[Circuit]:
    ciphers = [enc.encode_int(v, insize) for v in input]
    return ciphers

def main():
    parser = argparse.ArgumentParser(description="List comparison in binfhe"
                                                            , epilog=f"allowed contexts: binfhe")

    parser.add_argument("-is", "--insize", required=True, type=int, help="Size of the integers in the list")
    parser.add_argument("-ls", "--listsize", required=True, type=int, help="Size of the list of integers")
    parser.add_argument("-op", "--op", required=True, help="Program choices: Zip Less than or At least one equality", choices=["zip_lt", "any_eq"])
    parser.add_argument("--no-setup-runtime", default=False, action='store_true')

    config = parser.parse_args()

    list1 = make_randomlist(config.insize, config.listsize)
    list2 = make_randomlist(config.insize, config.listsize)

    with common.DisplayTime("setup", not config.no_setup_runtime) as _:
        (cc, sk) = context.binfhe_128()
        enc = BinFHEEncoder(cc, sk)

        cs1 = encrypt_list(enc, config.insize, list1)
        cs2 = encrypt_list(enc, config.insize, list2)

    with common.DisplayTime(f"runtime of {config.op}") as _:
        if config.op == "zip_lt":
            compare.zip_lt(cs1, cs2)
        elif config.op == "any_eq":
            compare.any_eq(cs1, cs2)
        else:
            raise NotImplementedError(f"The passed binFHE comparison program is not implemented: {config.prog}")



if __name__ == '__main__':
  main()