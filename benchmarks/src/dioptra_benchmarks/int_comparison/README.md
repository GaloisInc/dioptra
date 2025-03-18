# Integer comparison benchmarks:

Two different benchmarks are included in this directory:

- `any_eq` for two lists of the same size, are there any common integers between the two lists
- `zip_lt` for two lists (let's call them `A` and `B`) of the same size, is every element in `A` less than the corresponding element at the same index in `B`

To calibrate the context used in this benchmark, run:

```
python calibrate.py
```

This will add calibration data to the `context` subdirectory located here.  The existing calibration data is included as an example.

To run pre-configured benchmarks and estimates use the `run_benchmarks.py` script located in this directory.

Other files of interest:

- `main.py` contains the code for running the benchmark code in OpenFHE - use this for more fine grained control than `run_benchmarks.py`
- `compare.py` contains the actual benchmark code
- `estimates.py`  contain the dioptra estimates for selected input sizes
- `context.py` contains configuration information for the context used



