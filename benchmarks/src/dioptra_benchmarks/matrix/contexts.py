import matrix as matrix
from dioptra.context import dioptra_binfhe_context, dioptra_pke_context
import openfhe as ofhe
import benchmark.contexts as ctxts

@dioptra_pke_context()
def ckks_128():
  return ctxts.mk_ckks(ofhe.SecurityLevel.HEStd_128_classic)

@dioptra_pke_context()
def bgv_128():
  return ctxts.mk_bgv(pt_mod=65537, sec_level=ofhe.SecurityLevel.HEStd_128_classic, mult_depth=3)

@dioptra_pke_context()
def bfv_128():
  return ctxts.mk_bfv(pt_mod=65537, sec_level=ofhe.SecurityLevel.HEStd_128_classic, mult_depth=3)

@dioptra_binfhe_context()
def binfhe_128():
  return ctxts.mk_binfhe(ofhe.STD128)

contexts = {
  "ckks_128": (ckks_128, matrix.PkeFloatBuilder),
  "bgv_128": (bgv_128, matrix.PkeIntegerBuilder),
  "bfv_128": (bfv_128, matrix.PkeIntegerBuilder),
  "binfhe_128": (binfhe_128, matrix.BinBuilder)
}