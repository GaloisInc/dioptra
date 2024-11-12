"""Dioptra context decorators.

Definition of the `@dioptra_context()` and `@dioptra_binfhe_context()`
decorators used to mark FHE contexts for Dioptra's command-line tools.
"""

import inspect
from typing import Callable, OrderedDict

from dioptra.context.context_function import ContextFunction
from dioptra.utils.scheme_type import SchemeType

context_functions: OrderedDict[str, ContextFunction] = OrderedDict()


def _dioptra_context_decorator(
    description: str | None, f: Callable, ty: SchemeType
) -> Callable:
    d = f.__name__ if description is None else description
    if d in context_functions:
        other = context_functions[d]
        file = inspect.getfile(other.run)
        (_, line) = inspect.getsourcelines(other.run)
        raise ValueError(
            f"Context {d} has been defined earlier (at  ={file}:{line}) - use 'description' in decorator to rename?"
        )

    context_functions[d] = ContextFunction(d, f, ty)
    return f


def dioptra_context(description: str | None = None):
    """Mark a Diotpra PKE context for calibration.

    Keyword arguments:
    description -- a description of the context (default: none)

    Note that the description can be used to disambiguate contexts with the same
    function name.
    """

    def decorator(f):
        return _dioptra_context_decorator(description, f, SchemeType.PKE)

    return decorator


def dioptra_binfhe_context(description: str | None = None):
    """Mark a Diotpra PKE context for calibration.

    Keyword arguments:
    description -- a description of the context (default: none)

    Note that the description can be used to disambiguate contexts with the same
    function name.
    """

    def decorator(f):
        return _dioptra_context_decorator(description, f, SchemeType.BINFHE)

    return decorator
