import enum
from typing import Any

import openfhe


class BinFHEEventKind(enum.Enum):
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
    GENERATE_LUT_VIA_FUNCTION = 16


class BinFHEEvent:
    def __init__(self, kind: BinFHEEventKind):
        self.kind = kind

    def __hash__(self) -> int:
        return hash(self.kind.value)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, BinFHEEvent) and self.kind == value.kind

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind.value}

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "BinFHEEvent":
        kind = BinFHEEventKind(d["kind"])
        return BinFHEEvent(kind)

    def __str__(self) -> str:
        return f"{self.kind.name}"

    @staticmethod
    def bingate_to_event() -> dict[openfhe.BINGATE, "BinFHEEvent"]:
        if BinFHEEvent.BINGATE_TO_EVENT is None:
            BinFHEEvent.BINGATE_TO_EVENT = {
                openfhe.BINGATE.OR: BinFHEEvent(BinFHEEventKind.EVAL_BIN_GATE_OR),
                openfhe.BINGATE.AND: BinFHEEvent(BinFHEEventKind.EVAL_BIN_GATE_AND),
                openfhe.BINGATE.NOR: BinFHEEvent(BinFHEEventKind.EVAL_BIN_GATE_NOR),
                openfhe.BINGATE.NAND: BinFHEEvent(BinFHEEventKind.EVAL_BIN_GATE_NAND),
                openfhe.BINGATE.XOR_FAST: BinFHEEvent(
                    BinFHEEventKind.EVAL_BIN_GATE_XORFAST
                ),
                openfhe.BINGATE.XNOR_FAST: BinFHEEvent(
                    BinFHEEventKind.EVAL_BIN_GATE_XNORFAST
                ),
                openfhe.BINGATE.XOR: BinFHEEvent(BinFHEEventKind.EVAL_BIN_GATE_XOR),
                openfhe.BINGATE.XNOR: BinFHEEvent(BinFHEEventKind.EVAL_BIN_GATE_XNOR),
            }

        return BinFHEEvent.BINGATE_TO_EVENT

    BINGATE_TO_EVENT: dict[openfhe.BINGATE, "BinFHEEvent"] | None = None
