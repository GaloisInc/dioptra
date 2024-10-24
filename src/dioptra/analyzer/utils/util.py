import json
from typing import Iterator

from dioptra.analyzer.utils.code_loc import Frame, MaybeFrame

def format_bytes(bytes: int) -> str:
    if bytes / 10**3 < 1000:
        return f"{bytes/10**3:3f} KB"

    if bytes / 10**6 < 1000:
        return f"{bytes/10**6:3f} MB"

    if bytes / 10**9 < 1000:
        return f"{bytes/10**9:3f} GB"

    if bytes / 10**12 < 1000:
        return f"{bytes/10**12:3f} TB"

    return f"{bytes/10**15:3f} PB"


def format_ns_approx(ns: int) -> str:
    micro = ns / 1000
    milli = micro / 1000
    second = milli / 1000
    minute = second / 60
    hour = minute / 60
    day = hour / 24
    year = day / 365
    mil = year / 1000

    if mil > 2:
        return f"~{mil:3f} millenia"

    elif year > 2:
        return f"~{year:3f} years"

    elif day > 3:
        return f"~{day:3f} days"

    elif hour > 1:
        return f"~{hour:3f} hrs"

    elif minute > 3:
        return f"~{minute:3f} min"

    elif second > 1:
        return f"~{second:3f} s"

    elif milli > 1:
        return f"~{milli:3f} ms"

    elif micro > 1:
        return f"~{micro} us"

    else:
        return f"{ns} ns"


def format_ns(ns: int) -> str:
    micro = ns // 1000
    milli = micro // 1000
    second = milli // 1000
    minute = second // 60
    hour = minute // 60
    day = hour // 24
    year = day // 365
    mil = year // 1000

    if mil > 0:
        return f"{mil} millenia"

    tstr = f"{ns % 1000:03}ns"
    if micro > 0:
        tstr = f"{micro%1000:03}us" + tstr
    if milli > 0:
        tstr = f"{milli%1000:03}ms" + tstr
    if second > 0:
        tstr = f"{second%60:02}s" + tstr
    if minute > 0:
        tstr = f"{minute%60:02}m" + tstr
    if hour > 0:
        tstr = f"{hour%24:02}h" + tstr
    if day > 0:
        tstr = f"{day%365:03}d" + tstr
    if year > 0:
        tstr = f"{year:03}y" + tstr

    return tstr


# range function with step that always includes endpoints
def ep_range(start: int, end: int, step: int) -> Iterator[int]:
    i = start
    while i < end - 1:
        yield i
        i += step

    yield end - 1


def lerp(p1, p2, x):
    (x1, y1) = p1
    (x2, y2) = p2

    m = y2 - y1 // x2 - x1
    return y1 + m * (x1 - x)


def blerp(xs, ys, zs, p):
    (x1, x2) = xs
    (y1, y2) = ys
    (q11, q21, q12, q22) = zs
    (x, y) = p

    v1 = lerp((x1, q11), (x2, q21), x)
    v2 = lerp((x1, q12), (x2, q22), x)

    return lerp((y1, v1), (y2, v2), y)

