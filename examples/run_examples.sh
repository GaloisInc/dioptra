#!/bin/bash

# Add the name of calibrations and their corresponding example script.
# Repeat names of calibrations as necessary!
calibrations=(bgv1 binfhe1 ckks_small1)
examples=(matrix_mult_bgv boolean_binfhe decorator_example)

for i in "${!examples[@]}"; do
    echo "Running example: ${examples[i]}..."
    dioptra estimate report -cd "${calibrations[i]}.dc" "${examples[i]}.py"
    echo
done

echo "All examples run successfully."
