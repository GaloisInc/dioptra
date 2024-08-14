from typing import Iterator


def format_ns(ns: int) -> str:
  micro = ns // 1000
  milli = micro // 1000
  second = milli // 1000

  tstr = f"{ns % 1000:03}n"
  if micro > 0:
    tstr = f"{micro%1000:03}u" + tstr
  if milli > 0:
    tstr = f"{milli%1000:03}m" + tstr
  if second > 0:
    tstr = f"{second}s" + tstr

  return tstr

# range function with step that always includes endpoints
def ep_range(start: int, end: int, step: int) -> Iterator[int]:
  i = start
  while i < end - 1:
    yield i
    i += step

  yield end - 1
