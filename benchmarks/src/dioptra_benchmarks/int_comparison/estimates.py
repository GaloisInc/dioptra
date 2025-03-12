from typing import Callable
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from benchmark.circuit import BinFHEEncoder, Circuit, BinFHEWire, Wire
from dioptra.estimate import EstimationCases, dioptra_custom_estimation
from compare import any_eq, zip_lt

def mk_arbitrary_circuit(cc: BinFHEAnalyzer, sz: int) -> Circuit:
  return Circuit(list(BinFHEWire(cc, cc.ArbitraryCT()) for _ in range(sz)))

def mk_estimation_case(
    op: Callable[[list[Circuit], list[Circuit]], Wire],
    int_sz: int,
    list_size: int):
  def case(cc: BinFHEAnalyzer):
    cs1 = [mk_arbitrary_circuit(cc, int_sz) for _ in range(0, list_size)]
    cs2 = [mk_arbitrary_circuit(cc, int_sz) for _ in range(0, list_size)]
    op(cs1, cs2)
  
  return case

@dioptra_custom_estimation()
def estimates(ec: EstimationCases):
  for (name, op) in [("any_eq", any_eq), ("zip_lt", zip_lt)]:
    for int_sz in [8, 16, 32, 64]:
      for list_size in [8, 16, 32]:
        desc = f"{name} int_sz: {int_sz} list_size: {list_size}"
        ec.add_binfhe_case(mk_estimation_case(op, int_sz, list_size), desc)
