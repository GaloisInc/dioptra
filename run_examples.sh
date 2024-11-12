#!/bin/bash

# NOTE: Assumes you are in a Python environment with Dioptra installed!

if [[ "${#}" -ne 1 ]] || [[ ! "${1}" =~ ^(execute|estimate)$ ]]; then
    echo "Usage: ${0} <execute|estimate>"
    exit 1
fi

# Add entries to this dictionary for any additional examples
declare -A calibrations
calibrations["matrix_mult.bfv"]="bfv1 /estimates.py"
calibrations["nn.bfv"]="bfv1 /estimates.py"
calibrations["matrix_mult.bgv"]="bgv1 /estimates.py"
calibrations["nn.bgv"]="bgv1 /estimates.py"
calibrations["boolean_binfhe"]="binfhe1 .py"
calibrations["matrix_mult.ckks"]="ckks_small1 /estimates.py"
calibrations["nn.ckks"]="ckks_small1 /estimates.py"
calibrations["network.binfhe"]="binfhe1 .py"

if [[ "${1}" == "execute" ]]; then
    echo "Running examples in OpenFHE..."

    for example in "${!calibrations[@]}"; do
        echo "Running example: ${example}..."
        python -m "dioptra_examples.${example}"
        echo
    done
elif [[ "${1}" == "estimate" ]]; then
    echo "Estimating using Dioptra..."

    examples_root=examples/src/dioptra_examples

    for example in "${!calibrations[@]}"; do
        calibration="${calibrations[${example}]}"
        read -r calibration_context extra_path <<< "${calibration}"
        calibration_context="examples/${calibration_context}.dc"
        example_path="${examples_root}/${example//.//}${extra_path}"

        echo "Estimating cases in ${example_path}..."
        dioptra estimate report -cd "${calibration_context}" "${example_path}"
        echo
    done
fi
