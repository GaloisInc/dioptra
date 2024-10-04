from dioptra.analyzer.metrics.analysisbase import Analyzer
from dioptra.analyzer.utils.util import BPS
from dioptra.decorator import dioptra_runtime


@dioptra_runtime()
def network_example(a: Analyzer):
  network = a.MakeNetwork(
    send_bps=BPS(Mbps=100),
    recv_bps=BPS(Gbps=1),
    latency_ms=50
  )

  ct1 = a.ArbitraryCT(level=20)
  ct2 = a.ArbitraryCT()
  network.RecvCiphertext(ct1)
  network.RecvCiphertext(ct2)

  ct3 = a.EvalMult(ct1, ct2)

  network.SendCiphertext(ct3)