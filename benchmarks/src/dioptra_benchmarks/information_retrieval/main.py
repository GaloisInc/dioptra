import argparse
import math
import sys
from benchmark import common
from benchmark import circuit
import contexts
import pir
import openfhe as ofhe
import random

def size_bits(n: int) -> int:
  return math.ceil(math.lg2(n))

def encode_plaintext(cc: ofhe.CryptoContext, arr: list[int|float], is_ckks: bool) -> ofhe.Plaintext:
  if is_ckks:
    return cc.MakeCKKSPackedPlaintext(arr)
  else:
    return cc.MakePackedPlaintext(arr)

def random_pke_plaintext(cc: ofhe.CryptoContext, num_slots: int, is_ckks: bool) -> ofhe.Plaintext:
  if is_ckks:
    arr = list(random.random() for _ in range(0, num_slots))
    
  else:
    arr = list(random.randint(0, 60000) for _ in range(0, num_slots))
  
  return encode_plaintext(cc, arr, is_ckks)
  
def main():
  parser = argparse.ArgumentParser()
  allowed_contexts = ", ".join(sorted(contexts.contexts.keys()))
  parser = argparse.ArgumentParser( description="Private information retrieval benchmark"
                                  , epilog=f"allowed contexts: {allowed_contexts}")
  

  parser.add_argument("--context", required=True, help="Context to use to do the computation")
  parser.add_argument("--no-setup-runtime", default=False, action='store_true')

  subparsers = parser.add_subparsers(dest="benchmark", required=True)
  private_weighting = subparsers.add_parser("private_weighting")
  retrieve = subparsers.add_parser("retrieve", description="PIR retrieval benchmark")
  retrieve.add_argument("--database-size", type=int, required=True)
  retrieve.add_argument("--binfhe-result-size", type=int, default=16)

  args = parser.parse_args()

  if args.benchmark == "private_weighting":
    if contexts.is_binfhe(args.context):
      print("private weighting not implemented for binfhe context")
      sys.exit(1)

    with common.DisplayTime("Setup", not args.no_setup_runtime) as _:
      (cc, cfg, keys, _) = contexts.contexts[args.context]()

    query_ct = None
    slots = pir.num_slots(cc, cfg)
    with common.DisplayTime("Encode/Encrypt Query", not args.no_setup_runtime) as _:
      query_pt = random_pke_plaintext(cc, slots, contexts.is_ckks(args.context))
      query_ct = cc.Encrypt(keys.publicKey, query_pt)

    pke_pir = pir.PKE_PIR(cc, slots)

    with common.DisplayTime("Runtime:"):
      pke_pir.private_weighting(query_ct, 0)


  elif args.benchmark == "retrieve":
    if args.database_size <= 0:
      print("database size cannot be less than or equal to zero!")
      sys.exit(1)

    if args.binfhe_result_size <= 0:
      print("binfhe result size cannot be less than or equal to zero")

    if contexts.is_binfhe(args.context):
      bits = size_bits(args.database_size)

      with common.DisplayTime("Setup", not args.no_setup_runtime):
        (cc, keys) = contexts.contexts[args.context]()
        database = list(random.randint(0, 2**args.binfhe_result_size - 1) for _ in args.database_size)

      with common.DisplayTime("Encode/Encrypt Query", not args.no_setup_runtime):
        enc = circuit.BinFHEEncoder(cc, keys.privateKey)
        query_pt = random.randint(0, args.database_size - 1)
        query_circuit = enc.encode_int(query_pt, bits)
      
      with common.DisplayTime("Runtime:"):
        pir.pir_binfhe_retrieve(database, query_circuit)

    else:  # PKE context 
      with common.DisplayTime("Setup", not args.no_setup_runtime) as _:
        (cc, cfg, keys, _) = contexts.contexts[args.context]()

      slots = pir.num_slots(cc, cfg)
      if slots < args.database_size:
        print("Database size is larger than number of slots, entire database is not addressable")
        exit(1)

      query_ct = None
      with common.DisplayTime("Encode/Encrypt Query", not args.no_setup_runtime) as _:
        query_arr = [0] * args.database_size
        query_arr[random.randint(0, args.database_size - 1)] = 1

        query_pt = encode_plaintext(cc, query_arr, contexts.is_ckks(args.context))
        query_ct = cc.Encrypt(keys.publicKey, query_pt)

      slots = pir.num_slots(cc, cfg)
      pke_pir = pir.PKE_PIR(cc, slots)

      database: list[ofhe.Plaintext] = []
      with common.DisplayTime("Make database", not args.no_setup_runtime) as _:
        for _ in range(0, args.database_size):
          database.append(random_pke_plaintext(cc, slots, contexts.is_ckks(args.context)))

      with common.DisplayTime("Runtime:"):
        pke_pir.retrieve(database, query_ct)


if __name__ == '__main__':
  main()
  