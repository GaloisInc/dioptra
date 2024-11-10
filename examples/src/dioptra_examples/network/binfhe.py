"""BinFHE Network Estimation Example

This example shows a simple example of the dioptra's network estimation
feature for a binfhe computation.  It simulates the sending of two
ciphertexts over the network, after which an AND is performed.
Then, the result of the AND is "sent" back - the send also being
simulated.
"""

from dioptra.analyzer.binfhe.analyzer import BinFHEAnalyzer
from dioptra.analyzer.utils.util import BPS
from openfhe import BINGATE

from dioptra.decorator import dioptra_binfhe_runtime


@dioptra_binfhe_runtime()
def network_example(a: BinFHEAnalyzer):
    # definition of the network parameters
    network = a.MakeNetwork(send_bps=BPS(Mbps=100), recv_bps=BPS(Gbps=1), latency_ms=50)

    ct1 = a.ArbitraryCT()
    ct2 = a.ArbitraryCT()

    # simulate sending `ct1` and `ct2`
    network.RecvCiphertext(ct1)
    network.RecvCiphertext(ct2)

    # do a computation
    ct3 = a.EvalBinGate(BINGATE.AND, ct1, ct2)

    # simulate receiving the result
    network.SendCiphertext(ct3)
