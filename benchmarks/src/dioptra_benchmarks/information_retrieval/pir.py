from typing import Callable
import openfhe as ofhe
import random
from benchmark.circuit import Circuit, Wire

def ith_array(cc: ofhe.CryptoContext, q: ofhe.Ciphertext, i: int, ct_slots: int) -> ofhe.Ciphertext:
  # make a plaintext consisting of the array with 1 as its i-th element
  # and zero for everything else
  one_arr = [0] * ct_slots
  one_arr[i] = 1
  one_arr_pt = cc.MakePackedPlaintext(one_arr)

  # What follows is a essentially a dot product between the query and one_arr.
  # First we multiply q with one_arr_pt pointwise, resulting in q_2 - an array 
  # which is zero everywhere except at i, where it has the value of q[i]
  q_2 = cc.EvalMult(q, one_arr_pt)

  # Finally, we create the array where every slot is equal to the value of q[i]
  # by summing all the values in the array - this works because there is at most
  # one non-zero value in q_2 (which is q[i]) 
  return cc.EvalSum(q_2, ct_slots)

# Compute the number of slots in a ciphertext
def num_slots(cc: ofhe.CryptoContext, params: ofhe.CryptoParams) -> int:
  if isinstance(params, ofhe.CryptoParamsCKKSRNS):
    return cc.GetRingDimension() / 2
  else:
    return cc.GetRingDimension()

def pir_pke_lookup(cc: ofhe.CryptoContext, database: list[int|float], query: ofhe.Ciphertext, ct_slots: int) -> ofhe.Ciphertext:
  result = None
  for idx in range(0, len(database)):
    ith = ith_array(cc, query, idx, ct_slots)
    if result is None:
      result = cc.EvalMult(ith, database[idx])
    else:
      result = cc.EvalAdd(cc.EvalMult(ith, database[idx]), result)
  
  return result

# Takes a conjunction of queries 
def pir_binfhe_lookup(database: list[(list[int], int)], query: list[Circuit]) -> (Wire, Circuit):
  assert(len(query) > 0)
  zero = query[0].zero()
  
  match: Wire = zero
  result: Circuit = query[0].plain(0, 16)
  
  criteria: list[int]
  data: list[int]
  for (criteria, data) in database:
    assert(len(criteria) == len(query))

    criteriaMatch: Wire = None
    for q, c in zip(query, criteria):
      c_circuit = q.plain(c)
      criteriaMatch = q.eq(c_circuit) if criteriaMatch is None else q.eq(c_circuit) & criteriaMatch

    # if this is the first result, return it
    result = (~match & criteriaMatch).cond(data, result)
    match = criteriaMatch & match

  return (match, result)


