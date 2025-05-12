from typing import Callable
from dioptra.estimate import EstimationCases, dioptra_custom_estimation, dioptra_pke_estimation
from dioptra.pke.analyzer import Analyzer
import pir

def pke_pir_case(size: int) -> Callable[[Analyzer], None]:
  def run_case(cc: Analyzer) -> None:
    # `size` should be the number of CT slots but for the time being it doesn't matter to the estimator
    db = list(cc.ArbitraryPT() for x in range(0, size))
    pke_pir = pir.PKE_PIR(cc, size)
    query = cc.ArbitraryCT()
    pke_pir.retrieve(db, query)

  return run_case 

@dioptra_pke_estimation()
def pke_pir_weighted(cc: Analyzer):
  pke_pir = pir.PKE_PIR(cc, 1)
  query = cc.ArbitraryCT()
  pke_pir.private_weighting(query, 0)

@dioptra_custom_estimation()
def pke_pir_retrieve_estimates(ec: EstimationCases):
  for sz in [512,1024,2048]:
    ec.add_pke_case(pke_pir_case(sz), f"pke retrieve [database size {sz}]")