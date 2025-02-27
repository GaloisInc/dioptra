Perceptron benchmarks:

To calibrate the context used in this benchmark, run:

```
python calibrate.py
```

This will add calibration data to the `context` subdirectory located here.  The existing calibration data is included as an example.

To run pre-configured benchmarks and estimates use the `run_benchmarks.py` script located in this directory.

Other files of interest:

- `main.py` contains the code for running the benchmark code in OpenFHE - use this for more fine grained control than `run_benchmarks.py`
- `perceptron.py` contains the actual benchmark code
- `estimates.py`  contain the dioptra estimates for selected input sizes
- `context.py` contains configuration information for the context used



