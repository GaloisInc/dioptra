import datetime
from typing import Callable, Iterable

from dioptra.pke.analysisbase import Analyzer, Ciphertext
from dioptra.estimate import dioptra_runtime


# Three implementations of exponentiation
def ct_pow(cc: Analyzer, x: Ciphertext, y: int) -> Ciphertext:
    assert y > 0
    result = cc.EvalBootstrap(x)
    for i in range(1, y):
        result = cc.EvalMult(result, x)
        if i % 10 == 0:
            result = cc.EvalBootstrap(result)

    return result


def ct_pow_memo(
    cc: Analyzer, x: Ciphertext, y: int, memo: dict[tuple[Ciphertext, int], Ciphertext]
) -> Ciphertext:
    result = memo.get((x, y), None)
    if result is not None:
        return result

    result = ct_pow(cc, x, y)
    memo[(x, y)] = result
    return result


def ct_pow_memo_rec(
    cc: Analyzer, x: Ciphertext, y: int, memo: dict[tuple[Ciphertext, int], Ciphertext]
) -> Ciphertext:
    assert y > 0

    if y == 1:
        return cc.EvalBootstrap(x)

    result = memo.get((x, y), None)
    if result is not None:
        return result

    result = cc.EvalMult(ct_pow_memo_rec(cc, x, y - 1, memo), x)
    if y % 10 == 0:
        result = cc.EvalBootstrap(x)

    memo[(x, y)] = result
    return result


def ct_sum(cc: Analyzer, lst: Iterable[Ciphertext]) -> Ciphertext:
    result = None
    for elt in lst:
        if result is None:
            result = elt
        else:
            result = cc.EvalAdd(result, elt)

    assert result is not None, "ct_sum: argument list is empty"
    return result


# evaluate a polynomial given a function pow that can do exponentiation
def pow_perf(
    cc: Analyzer, pow: Callable[[Analyzer, Ciphertext, int], Ciphertext]
) -> None:
    x = cc.ArbitraryCT()

    terms = [
        pow(cc, x, 2),
        cc.EvalAdd(pow(cc, x, 3), pow(cc, x, 3)),
        pow(cc, x, 4),
        pow(cc, x, 8),
        pow(cc, x, 12),
    ]

    ct_sum(cc, terms)


# Compare the three implementations


@dioptra_runtime(limit=datetime.timedelta(minutes=4))
def eval_pow(cc: Analyzer) -> None:
    pow_perf(cc, ct_pow)


@dioptra_runtime(limit=datetime.timedelta(minutes=4))
def eval_pow_memo(cc: Analyzer) -> None:
    memo_table = {}

    def pow(_cc, x, y):
        return ct_pow_memo(_cc, x, y, memo_table)

    pow_perf(cc, pow)


@dioptra_runtime(limit=datetime.timedelta(minutes=4))
def eval_pow_memo_rec(cc: Analyzer) -> None:
    memo_table = {}

    def pow(_cc, x, y):
        return ct_pow_memo_rec(_cc, x, y, memo_table)

    pow_perf(cc, pow)
