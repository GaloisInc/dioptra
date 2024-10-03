#!/bin/false
# NOTE: This shebang prevents direct execution; use `source setup_env.sh` instead!

##### Setup Python environment #####

echo "Creating a Python venv..."
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip

##### Install dioptra_native to environment #####

echo "Building and installing dioptra_native to the environment..."
cd dioptra_native
mkdir build
cd build
cmake -DOpenFHE_DIR=/usr/local/lib/OpenFHE ..
make
cp *.so ../../venv/lib/python3.12/site-packages # TODO: There may be a better way.
cd ../..

##### Install dioptra #####

echo "Installing dioptra..."
pip install --editable .
