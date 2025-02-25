from dioptra.context import dioptra_pke_context
import openfhe as ofhe
import benchmark.contexts as ctxts

@dioptra_pke_context()
def ckks_128():
  return ctxts.mk_ckks(ofhe.SecurityLevel.HEStd_128_classic)
