from dioptra.analyzer.pke.analysisbase import Analyzer, Ciphertext
from dioptra.analyzer.pke.multdepth import MultDepth
from dioptra.analyzer.pke.scheme import SchemeModelCKKS


def runexample(fun) -> None:  # type: ignore
    md = MultDepth()
    analyzer = Analyzer([md], SchemeModelCKKS(2))
    fun(analyzer)


def square(crypto_context: Analyzer, c1: Ciphertext) -> Ciphertext:
    return crypto_context.EvalMult(c1, c1)


@runexample
def example(crypto_context: Analyzer) -> None:
    ciphertext1 = crypto_context.ArbitraryCT()
    ciphertext2 = crypto_context.ArbitraryCT()

    v = crypto_context.EvalMult(ciphertext1, ciphertext2)
    v2 = crypto_context.EvalAdd(v, v)
    crypto_context.EvalSub(v, v2)
    crypto_context.EvalMult(v, ciphertext1)
    v6 = square(crypto_context, v)
    square(crypto_context, v6)
