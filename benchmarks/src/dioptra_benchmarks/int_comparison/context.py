from dioptra.context import dioptra_binfhe_context
import openfhe as ofhe
import benchmark.contexts as ctxts

@dioptra_binfhe_context()
def binfhe_128():
  return ctxts.mk_binfhe(ofhe.STD128)
