# Private information retrieval multiplication benchmarks:

The PKE implementation computes a kind of linear combination of the database, while the BinFHE implementation returns exactly the value
matching the index.

To calibrate all contexts used in this benchmark, run:

```
python calibrate.py
```

This will add calibration data to the `contexts` subdirectory located here.  The existing calibration data is included as an example.

To run pre-configured benchmarks and estimates use the `run_benchmarks.py` script located in this directory.

Other files of interest:

- `main.py` contains the code for running the benchmark code in OpenFHE - use this for more fine grained control than `run_benchmarks.py`
- `pir.py` contains the actual benchmark code
- `binfhe_estimates.py`, `pke_estimates.py` contain the dioptra estimates for selected PIR database sizes
- `contexts.py` contains configuration information for each of the contexts used and allows new contexts to be added easily
- `benchmark/circuit.py` (which is a symlink to `../benchmark/circuit.py`) contains the code for building circuits with binfhe (including such things as modular addition and multiplication)



