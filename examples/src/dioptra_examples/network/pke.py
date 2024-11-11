"""PKE Network Estimation Example

This example shows a simple example of the dioptra's network estimation
feature for a binfhe computation.  It simulates the sending of two
ciphertexts over the network, after which the product of the two is
computed.  Then, the product is "sent" back - the send also being
simulated.
"""

from dioptra.estimate import dioptra_estimation
from dioptra.pke.analyzer import Analyzer
from dioptra.utils.measurement import BPS


@dioptra_estimation()
def network_example(a: Analyzer):
    # definition of the network parameters
    network = a.MakeNetwork(send_bps=BPS(Mbps=100), recv_bps=BPS(Gbps=1), latency_ms=50)

    ct1 = a.ArbitraryCT()
    ct2 = a.ArbitraryCT()

    # simulate sending `ct1` and `ct2`
    network.RecvCiphertext(ct1)
    network.RecvCiphertext(ct2)

    # compute the product
    ct3 = a.EvalMult(ct1, ct2)

    # simulate receiving the result
    network.SendCiphertext(ct3)
