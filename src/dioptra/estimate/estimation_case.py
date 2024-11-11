import datetime
import sys
from typing import Callable

from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.pke.analyzer import Analyzer
from dioptra.utils.error import NotSupportedException
from dioptra.scheme_type import SchemeType


class EstimationCase:
    def __init__(
        self,
        desc: str,
        f: Callable,
        schemetype: SchemeType,
        limit: datetime.timedelta | None,
    ):
        self.description = desc
        self.run = f
        self.schemetype = schemetype
        self.limit = limit

    def run_and_exit_if_unsupported(self, a: Analyzer | BinFHEAnalyzer) -> None:
        try:
            self.run(a)
        except NotSupportedException as e:
            print("Analysis failed:")
            print(f"  { e.display()}")
            sys.exit(1)
