# Class for displaying runtime of a chunk of code
# To be used with python's `with` syntax
import time
import dioptra.utils.measurement

class DisplayTime:
    def __init__(self, p: str, display: bool = True):
        self.display = display
        self.p = p

    def __enter__(self):
        self.start = time.time_ns()
        return self

    def __exit__(self, *arg):
        end = time.time_ns()
        if self.display:
            print(f"{self.p}: {dioptra.utils.measurement.format_ns_approx(end - self.start)}")
