from typing import Iterator



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
