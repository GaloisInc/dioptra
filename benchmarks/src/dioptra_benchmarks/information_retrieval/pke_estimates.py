from typing import Callable
from dioptra.estimate import EstimationCases, dioptra_custom_estimation
from dioptra.pke.analyzer import Analyzer
import pir

def pke_pir_case(size: int) -> Callable[[Analyzer], None]:
  db = list(x for x in range(0, size))
  def run_case(cc: Analyzer) -> None:
    query = cc.ArbitraryCT()
    # `size` should be the number of CT slots but for the time being it doesn't matter
    pir.pir_pke_lookup(cc, db, query, size)

  return run_case 

@dioptra_custom_estimation()
def binfhe_pir_estimates(ec: EstimationCases):
  for sz in [512,1024,2048]:
    ec.add_pke_case(pke_pir_case(sz), f"pir_binfhe_lookup [database size {sz}]")