#!/bin/sh

dioptra context calibrate examples/contexts.py -n ckks_small1 -o examples/ckks_small1.dc
dioptra context calibrate examples/contexts.py -n bfv1 -o examples/bfv1.dc
dioptra context calibrate examples/contexts.py -n bgv1 -o examples/bgv1.dc
dioptra context calibrate examples/contexts.py -n  binfhe1 -o examples/binfhe1.dc