from dioptra.context import dioptra_binfhe_context
import openfhe as ofhe
import benchmark.contexts as ctxts

def ckks_128():
  return ctxts.mk_ckks(ofhe.SecurityLevel.HEStd_128_classic)
