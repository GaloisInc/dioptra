from dioptra.analyzer.binfhe.analyzer import BinFHEAnalyzer
from dioptra.analyzer.utils.util import BPS
from openfhe import BINGATE

from dioptra.decorator import dioptra_binfhe_runtime


@dioptra_binfhe_runtime()
def network_example(a: BinFHEAnalyzer):
  network = a.MakeNetwork(
    send_bps=BPS(Mbps=100),
    recv_bps=BPS(Gbps=1),
    latency_ms=50
  )

  ct1 = a.ArbitraryCT()
  ct2 = a.ArbitraryCT()
  network.RecvCiphertext(ct1)
  network.RecvCiphertext(ct2)

  ct3 = a.EvalBinGate(BINGATE.AND, ct1, ct2)

  network.SendCiphertext(ct3)