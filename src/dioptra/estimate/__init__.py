import datetime
import inspect
from typing import Callable, OrderedDict

from dioptra.estimate.estimation_case import EstimationCase
from dioptra.scheme_type import SchemeType

estimation_cases: OrderedDict[str, EstimationCase] = OrderedDict()


def _estimation_case_decorator(
    description: str | None,
    f: Callable,
    limit: datetime.timedelta | None,
    ty: SchemeType,
) -> Callable:
    d = f.__name__ if description is None else description
    if d in estimation_cases:
        other = estimation_cases[d]
        file = inspect.getfile(other.run)
        (_, line) = inspect.getsourcelines(other.run)
        raise ValueError(
            f"Estimation case {d} has been defined earlier (at  ={file}:{line}) - use 'description' in decorator to rename?"
        )

    estimation_cases[d] = EstimationCase(d, f, ty, limit)
    return f


def dioptra_runtime(
    limit: datetime.timedelta | None = None, description: str | None = None
) -> Callable:  # TODO better type
    def decorator(f):
        _estimation_case_decorator(description, f, limit, SchemeType.PKE)

    return decorator


def dioptra_binfhe_runtime(
    limit: datetime.timedelta | None = None, description: str | None = None
) -> Callable:  # TODO better type
    def decorator(f):
        _estimation_case_decorator(description, f, limit, SchemeType.BINFHE)

    return decorator
