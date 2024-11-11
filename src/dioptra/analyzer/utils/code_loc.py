import inspect
import dis
import sys
from typing import Any, Iterable, Optional, Self


class SourceLocation:
    def __init__(self, filename: str, loc: dis.Positions):
        self.is_unknown = False
        self.filename = filename
        self.position = loc

    @staticmethod
    def unknown() -> "SourceLocation":
        sl = SourceLocation("unknown", dis.Positions())
        sl.is_unknown = True
        return sl

    def __str__(self) -> str:
        if self.is_unknown:
            return f"<location unknown?>"
        else:
            return f"{self.filename}:{self.position.lineno}:{self.position.col_offset}"

    def __hash__(self) -> int:
        if self.is_unknown:
            return hash((False, None, None))
        else:
            return hash((True, self.filename, self.position))

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SourceLocation) or self.is_unknown != value.is_unknown:
            return False

        elif self.is_unknown:
            return True

        return self.filename == value.filename and self.position == value.position


class StackLocation:
    def __init__(self, loc: SourceLocation, fn_name: str):
        self.source_location = loc
        self.function_name = fn_name

    def __hash__(self) -> int:
        return hash((self.source_location, self.function_name))

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, StackLocation)
            and self.source_location == value.source_location
            and self.function_name == value.function_name
        )

    def __str__(self) -> str:
        return f"{self.function_name} at {self.source_location}"


class Frame:
    def __init__(self, frame):
        if frame is None:
            raise ValueError("Frame should not be none")
        self.frame = frame
        cur_frame = inspect.getframeinfo(self.frame)
        self.filename = cur_frame.filename
        self.positions = cur_frame.positions
        self.fn_name = cur_frame.function

    def caller(self) -> Optional["Frame"]:
        if self.frame.f_back is None:
            return None
        return Frame(self.frame.f_back)

    # TODO: deprecate
    def location(self) -> tuple[str, dis.Positions | None]:
        return (self.filename, self.positions)

    def source_location(self) -> SourceLocation:
        if self.positions is None:
            return SourceLocation.unknown()
        else:
            return SourceLocation(self.filename, self.positions)

    def stack_location(self) -> list[StackLocation]:
        lst = []
        frame: Optional["Frame"] = self
        while frame is not None:
            lst.append(StackLocation(frame.source_location(), frame.fn_name))
            frame = frame.caller()

        return lst


class MaybeFrame:
    def __init__(self, frame: Frame | None):
        self.frame = frame

    def get_frame(self) -> Frame | None:
        return self.frame

    def caller(self) -> "MaybeFrame":
        if self.frame is None:
            return self
        else:
            return MaybeFrame(self.frame.caller())

    def source_location(self) -> SourceLocation:
        if self.frame is None:
            return SourceLocation.unknown()
        else:
            return self.frame.source_location()

    @staticmethod
    def current() -> "MaybeFrame":
        cur_frame = inspect.currentframe()
        if cur_frame is None:
            return MaybeFrame(None)

        return MaybeFrame(Frame(cur_frame))


# Find the stack frame of calling fn if it exists
def calling_frame() -> Frame | None:
    cur_frame = inspect.currentframe()
    if cur_frame is None:
        return None
    else:
        return Frame(cur_frame.f_back).caller()


class TraceLoc:
    def __init__(self):
        self.stack = []
        self.prev_trace = None

    def __enter__(self):
        self.prev_trace = sys.gettrace()
        sys.settrace(self.trace)
        TraceLoc.current_traceloc = self

    def __exit__(self, type, val, tb):
        sys.settrace(self.prev_trace)

    def get_current_frame(self) -> Frame | None:
        if len(self.stack) == 0:
            return None

        return Frame(self.stack[-1])

    def trace(self, frame, event: str, arg: Any):
        if event == "call":
            frame.f_trace_lines = False
            self.stack.append(frame)

        if event == "return":
            self.stack.pop()

        return self.trace
