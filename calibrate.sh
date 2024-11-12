#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: ${0} /path/to/contexts.py /path/to/calibrations"
    exit 1
fi

mkdir -p "${2}"

dioptra context list "${1}" | while read -r context_with_loc; do
    context_fun=$(echo "$context_with_loc" | awk '{print $1;}')
    dioptra context calibrate "${1}" -n "${context_fun}" -o "${2}/${context_fun}.dc"
done
