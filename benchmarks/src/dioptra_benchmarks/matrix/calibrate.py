import os
import sys
import contexts
import pathlib

loc = pathlib.Path(__file__).parent
calibration_loc = loc.joinpath("calibration").absolute()
contexts_loc = loc.joinpath("contexts.py")

def calibrate(ctx_name):
  output_loc = calibration_loc.joinpath(f"{ctx_name}.cd")
  cmd = f"dioptra context calibrate --name {ctx_name} -o \"{output_loc}\" \"{contexts_loc}\""
  print(cmd)
  os.system(cmd)
  
def main():
  args = sys.argv[1:]

  bad_args = list(arg for arg in args if arg not in contexts.contexts.keys())
  if len(bad_args) > 0:
    print(f"contexts not recognized: {",".join(bad_args)}", file=sys.stderr)
    sys.exit(1)

  arg_set = set(args)
  for ctx in contexts.contexts.keys():
    if len(args) == 0 or ctx in arg_set:
      calibrate(ctx)

if __name__ == '__main__':
  os.chdir(pathlib.Path(__file__).parent)
  main()