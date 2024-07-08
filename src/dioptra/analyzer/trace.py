import sys

class Zookie:
    def __init__(self, i: int) -> None:
        self.i = i

# def f1(z: Zookie) -> Zookie:
#   return Zookie(z.i + 1)

# def f2(z1: Zookie, z2: Zookie) -> Zookie:
#   return Zookie(z1.i + z2.i)

# def f3(z: Zookie, v: int) -> Zookie:
#   result = Zookie(0)
#   for _i in range(0, v):
#      result = f2(result, z)

def bla (z: Zookie) -> Zookie:
   z2 = Zookie(z.i * z.i)
   return z2
  # return result
def square(z: Zookie) -> Zookie:
   return bla(z)


def main() -> None:
   _z = Zookie(2)
   _z2 = square(_z) 
   _zookie = square(_z2)


#######################

def trace(frame, event: str, arg: any): # type: ignore
  if event == "return":
    if isinstance(arg, Zookie):
        print(f"Zookie return at {frame.f_back} with value {arg.i}") #type: ignore

  return trace

def run() -> None:
  sys.settrace(trace)
  main()
