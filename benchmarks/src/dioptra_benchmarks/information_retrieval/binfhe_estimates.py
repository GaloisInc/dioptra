from typing import Callable
from benchmark.circuit import BinFHEEncoder, BinFHEWire, Circuit
import dioptra.binfhe
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.estimate import EstimationCases, dioptra_custom_estimation
import pir
import dioptra

def arbitrary_circuit(cc: BinFHEAnalyzer, sz: int) -> Circuit:
  wires = [BinFHEWire(cc, cc.ArbitraryCT()) for _ in range(0, sz)]
  return Circuit(wires)

def binfhe_retrieve_case(bits: int) -> Callable[[BinFHEAnalyzer], None]:
  def run_case(cc: BinFHEAnalyzer):
    db_size = 2 ** bits
    database = list(x * x for x in range(0, db_size))
    query = arbitrary_circuit(cc, bits)
    pir.pir_binfhe_retrieve(database, query, bits)

  return run_case

@dioptra_custom_estimation()
def binfhe_pir_estimates(ec: EstimationCases):
  for bits in [4, 6, 8, 10]:
    ec.add_binfhe_case(binfhe_retrieve_case(bits), f"pir_binfhe_lookup [database size {2**bits}]")
