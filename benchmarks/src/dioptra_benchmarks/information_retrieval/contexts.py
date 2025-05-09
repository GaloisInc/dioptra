from dioptra.context import dioptra_binfhe_context, dioptra_pke_context
import openfhe as ofhe
import benchmark.contexts as ctxts

@dioptra_pke_context()
def bfv_128():
  return ctxts.mk_bfv(pt_mod=65537, sec_level=ofhe.SecurityLevel.HEStd_128_classic, mult_depth=3)

@dioptra_binfhe_context()
def binfhe_128():
  return ctxts.mk_binfhe()

contexts = {
  "bfv_128": bfv_128,
  "binfhe_128": binfhe_128,
}
