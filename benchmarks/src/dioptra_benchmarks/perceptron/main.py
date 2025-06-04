import sys
from perceptron import *

# Runner to test actual runtime against
def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} INPUTSIZE")
        sys.exit(1)
    i = int(sys.argv[1])
    run_single_perception_cc(i)

if __name__ == "__main__":
    main()