import inspect

# Find the stack frame of calling fn if it exists
def calling_frame() -> inspect.Traceback | None:
    cur_frame = inspect.currentframe()
    if cur_frame is None:
        return None
    else: 
        caller = cur_frame.f_back
        if caller is not None and caller.f_back is not None:
            return inspect.getframeinfo(caller.f_back)
        return None
