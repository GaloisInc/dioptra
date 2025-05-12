from typing import Callable
import openfhe as ofhe
import random
from benchmark.circuit import Circuit, Wire


# Compute the number of slots in a ciphertext
def num_slots(cc: ofhe.CryptoContext, params) -> int:
  if isinstance(params, ofhe.CryptoParamsCKKSRNS):
    return cc.GetRingDimension() / 2
  else:
    return cc.GetRingDimension()

class PKE_PIR:
  def __init__(self, cc: ofhe.CryptoContext, slots: int) -> None:
    self.cc = cc
    self.num_slots = slots

  # Step 1: private weighting
  def private_weighting(self, q: ofhe.Ciphertext, i: int) -> ofhe.Ciphertext:
    """make a plaintext consisting of the array with q[i] for all of its entries"""
    one_arr = [0] * self.num_slots
    one_arr[i] = 1
    one_arr_pt = self.cc.MakePackedPlaintext(one_arr)

    # What follows is a essentially a dot product between the query and one_arr.
    # First we multiply q with one_arr_pt pointwise, resulting in q_2 - an array 
    # which is zero everywhere except at i, where it has the value of q[i]
    q_2 = self.cc.EvalMult(q, one_arr_pt)

    # Finally, we create the array where every slot is equal to the value of q[i]
    # by summing all the values in the array - this works because there is at most
    # one non-zero value in q_2 (which is q[i]) 
    return self.cc.EvalSum(q_2, self.num_slots)

  # Step 2: retrieval
  def retrieve(self, database: list[ofhe.Plaintext], query: ofhe.Ciphertext) -> ofhe.Ciphertext:
    result = None
    for idx in range(0, len(database)):
      ith = self.private_weighting(query, idx)
      query_entry_weight = self.cc.EvalMult(ith, database[idx])
      result = query_entry_weight if result is None else self.cc.EvalAdd(query_entry_weight, result)
    
    return result

def pir_binfhe_retrieve(database: list[int], query: Circuit, result_size: int) -> Circuit:
  """Look up single value in `database`"""
  zero = query.zero()
  
  match: Wire = zero
  result: Circuit = query.plain(0, result_size)

  for idx in range(0, len(database)):
    entry_value = query.plain(database[idx])
    is_query_entry = query.eq(query.plain(idx))
    result = is_query_entry.cond(entry_value, result)

  return result

# Takes a conjunction of queries 
def pir_binfhe_conj_retrieve(database: list[tuple[list[int], int]], query: list[Circuit]) -> tuple[Wire, Circuit]:
  assert(len(query) > 0)
  zero = query[0].zero()
  
  match: Wire = zero
  result: Circuit = query[0].plain(0, 16)
  
  criteria: list[int]
  data: int
  for (criteria, data) in database:
    assert(len(criteria) == len(query))

    criteriaMatch: Wire = None
    for q, c in zip(query, criteria):
      c_circuit = q.plain(c)
      criteriaMatch = q.eq(c_circuit) if criteriaMatch is None else q.eq(c_circuit) & criteriaMatch

    # if this is the first result, return it
    result = (~match & criteriaMatch).cond(result.plain(data), result)
    match = criteriaMatch & match

  return (match, result)


