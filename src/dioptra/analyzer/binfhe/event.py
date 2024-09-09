import enum

class EventKind(enum.Enum):
  ENCRYPT = 0
  DECRYPT = 1
  EVAL_BIN_GATE_OR = 2
  EVAL_BIN_GATE_AND = 3
  EVAL_BIN_GATE_NOR = 4
  EVAL_BIN_GATE_NAND = 5
  EVAL_BIN_GATE_XORFAST = 6
  EVAL_BIN_GATE_XNORFAST = 7
  EVAL_BIN_GATE_XOR = 8
  EVAL_BIN_GATE_XNOR = 9
  EVAL_DECOMP = 10
  EVAL_FLOOR = 11
  EVAL_FUNC = 12
  EVAL_NOT = 13
  EVAL_SIGN = 14
  KEYGEN = 15

class Event:
  def __init__(self, kind: EventKind):
    self.kind = kind