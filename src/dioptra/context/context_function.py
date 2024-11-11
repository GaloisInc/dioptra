from typing import Callable

from dioptra.utils.scheme_type import SchemeType


class ContextFunction:
    def __init__(self, desc: str, f: Callable, schemetype: SchemeType):
        self.description = desc
        self.run = f
        self.schemetype = schemetype
