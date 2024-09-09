class Value:
  id: int = 0

  def __init__(self):
    Value.id += 1
    self.value_id = Value.id
    
class LWECiphertext(Value):
  def __init__(self, length: int, modulus: int):
    super().__init__()
    self.length = length
    self.ct_mod = modulus
    self.pt_mod = 4

  def GetLength(self) -> int:
    return self.length
  
  def GetModulus(self) -> int:
    return self.ct_mod


class LWEPrivateKey(Value):
  def __init__(self, length: int):
    super().__init__()
    self.length = length

  def GetLength(self) -> int:
    return self.length
