"""Dioptra estimation decorators.

Definitions of the `@dioptra_pke_estimation()` and
`@dioptra_binfhe_estimation()` decorators used to mark estimation cases for
Dioptra's command-line tools.
"""

import datetime
import inspect
from typing import Callable, OrderedDict

from dioptra.estimate.estimation_case import EstimationCase
from dioptra.utils.scheme_type import SchemeType

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


def dioptra_pke_estimation(
    limit: datetime.timedelta | None = None, description: str | None = None
) -> Callable:
    """Mark a Dioptra PKE estimation case.

    Keyword arguments:
    limit -- the time limit for this estimation case (default: no limit)
    description -- a description of the estimation case (default: none)

    Note that the description can be used to disambiguate estimation cases with
    the same function name.
    """

    def decorator(f):
        _estimation_case_decorator(description, f, limit, SchemeType.PKE)

    return decorator


def dioptra_binfhe_estimation(
    limit: datetime.timedelta | None = None, description: str | None = None
) -> Callable:
    """Mark a Dioptra BinFHE estimation case.

    Keyword arguments:
    limit -- the time limit for this estimation case (default: no limit)
    description -- a description of the estimation case (default: none)

    Note that the description can be used to disambiguate estimation cases with
    the same function name.
    """

    def decorator(f):
        _estimation_case_decorator(description, f, limit, SchemeType.BINFHE)

    return decorator

class EstimationCases:
    """Allow the addition of estimation cases using the `dioptra_custom_estimation` 
    decorator.
    """
    def add_binfhe_case(self, f: Callable, description: str, limit: datetime.timedelta | None = None):
        """Add a binfhe estimation case"""      
        _estimation_case_decorator(description, f, limit, SchemeType.BINFHE)

    def add_pke_case(self, f: Callable, description: str, limit: datetime.timedelta | None = None):
        """Add a pke estimation case"""
        _estimation_case_decorator(description, f, limit, SchemeType.PKE)

def dioptra_custom_estimation() -> Callable:
    def decorator(f):
        f(EstimationCases())

    return decorator
