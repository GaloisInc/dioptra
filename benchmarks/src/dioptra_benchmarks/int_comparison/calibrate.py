import os
import sys
import pathlib

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
contexts_loc = loc.joinpath("context.py")

def calibrate():
  output_loc = calibration_loc.joinpath(f"binfhe_128.cd")
  cmd = f"dioptra context calibrate --name binfhe_128 -o \"{output_loc}\" \"{contexts_loc}\""
  print(cmd)
  os.system(cmd)
  
def main():
  calibrate()

if __name__ == '__main__':
  os.chdir(pathlib.Path(__file__).parent)
  main()