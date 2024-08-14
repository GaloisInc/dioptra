import inspect
import dis
from typing import Self

class Frame():
    def __init__(self, frame): #type: ignore
        if frame is None:
            raise("Frame should not be none")
        self.frame = frame
        cur_frame = inspect.getframeinfo(self.frame)
        self.filename = cur_frame.filename
        self.positions = cur_frame.positions

    def caller(self) -> Self | None:
        if self.frame.f_back is None:
            return None
        return Frame(self.frame.f_back)

    def location(self) -> tuple[str, dis.Positions]:
        return (self.filename, self.positions)
        
# Find the stack frame of calling fn if it exists
def calling_frame() -> Frame | None:
    cur_frame = inspect.currentframe()
    if cur_frame is None:
        return None
    else: 
        return Frame(cur_frame.f_back)


def frame_loc(frame) -> str:
    tb: inspect.Traceback = inspect.getframeinfo(frame)
    return f"{tb.filename}:{tb.positions.lineno}:{tb.positions.col_offset}"

def _trace(frame: any, event: str, arg: any):
    if event == 'call':
        caller = frame.f_back
        print(f"calling {frame.f_code.co_qualname} at {frame_loc(caller)}")

    if event == 'return' and frame.f_back is not None:
        caller = frame.f_back
        print(f"return from {frame.f_code.co_qualname} to {caller.f_code.co_qualname} at {frame_loc(caller)}")

    return _trace
