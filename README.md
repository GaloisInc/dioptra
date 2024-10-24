# Dioptra: FHE Performance Estimation

Dioptra is a Python library and command-line application for the analysis of
runtime and memory properties of Python code utilizing the OpenFHE libraries.

Dioptra works as follows:

1. A calibration file is produced for your system, providing baseline
   measurements on which all other estimations will be based
2. Code to be analyzed is decorated with one of a small handful of Python
   function decorators
3. Dioptra is run with the calibration data and Python source to produce a
   report on the terminal window, or an annotated version of the source

See `examples/` for concrete examples of calibrations and decorated source files
implementing a variety of FHE applications.

## Installation

**Disclaimer:** The following has only been tested on Darwin/OSX and Linux
systems, and there is no intention to support Windows at this time.
If you encounter any problems, please let us know!

We provide a `Dockerfile` describing an image that will handle the installation
of OpenFHE, its Python bindings, all necessary Python packages, and the Dioptra
sources. Please read [the Docker README](README.Docker.md) for more detailed
instructions on building and using this image.

## Checking the installation

The easiest way to check that the installation proceeded as expected is to
enter the `examples` directory and run `./run_examples.sh`. If this produces a
series of reports without error, you are ready to use Dioptra.

## Using Dioptra

### Calibrating for your system

Dioptra bases its estimates on calibration data collected for the specific
system under test. **Important!** This step necessitates running FHE operations
many times, which can take a significant amount of time. For a given choice of
FHE scheme and parameters, however, this process only needs to be completed once
for most applications.

For convenience, we provide the contexts necessary to calibrate Dioptra for your
system for a number of common schemes and parameter sets. These are defined in
`examples/contexts.py`, though you do not need to read or modify this file to
calibrate Dioptra on your system.

To view the available contexts for calibration, first run:

```console
> dioptra context list examples/contexts.py
```

Which will display the names of the available calibration contexts (and their
locations, if you need to adjust the parameters used).

Suppose you want to collect calibration data for CKKS. At time of writing, the
provided CKKS context we need is named `ckks1`. We run the following to actually
collect calibration data:

```console
> dioptra context calibrate --name ckks1 --output /path/to/calibrations/ckks.dc examples/contexts.py
```

By default, 5 samples will be used during calibration. You can change this
default using `--sample-count` (or the shorter `-sc`).

Remember that this might take a long time, depending on the scheme and parameter
set selected, but only needs to be run once for most applications (and, the
calibration data for your system / the system of interest may be shared with
other Dioptra users for their own estimation experiments).

### Estimating runtime and memory performance

Suppose we have the following Python function implementing matrix multiplication
under FHE, using CKKS:

```python
def matrix_mult(
    cc: ofhe.CryptoContext,
    x: list[list[ofhe.Ciphertext]],
    y: list[list[ofhe.Ciphertext]],
):
    assert len(x[0]) == len(y)

    rows = len(x)
    cols = len(y[0])
    l = len(x[0])

    result = [[0 for _ in range(rows)] for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            sum = cc.MakeCKKSPackedPlaintext([0])
            for k in range(l):
                mul = cc.EvalMult(x[i][k], y[k][j])
                sum = cc.EvalAdd(mul, sum)
            result[i][j] = sum
    return result
```

And, suppose we are interested in how this function will perform for 5x5
matrices. Furthermore, suppose we're going to setup the CKKS parameters to be
the same as those for which we earlier produced calibration data.

We can write the following function, which uses a Dioptra `Analyzer` object
where we might expect an `ofhe.CryptoContext`:

```python
@dioptra_runtime()
def report_runtime(cc: Analyzer):
    rows = 5
    cols = 5
    x_ct = [[cc.ArbitraryCT() for _ in range(cols)] for _ in range(rows)]
    y_ct = [[cc.ArbitraryCT() for _ in range(cols)] for _ in range(rows)]
    matrix_mult(cc, x_ct, y_ct)
```

The decorator is how Dioptra will know to trace this function's execution and
produce runtime and memory estimates. Notice that the `Analyzer` is passed to
`matrix_mult`: This means that all operations in `matrix_mult` using this object
will be considered during estimation.

The above is implemented in `examples/matrix_mult_ckks.py`. We can use our
calibrations from earlier to produce an estimate report using the following:

```console
> dioptra estimate report --calibration-data /path/to/calibrations/ckks.dc examples/matrix_mult_ckks.py
```

Which will output a wall-clock time estimate, and a maximum memory usage
estimate.

## For developers

There is a `.devcontainer` for VSCode development; this is virtually identical
to the project-level image, but designed to allow for real-time editing of the
source code. If you plan to modify any Dioptra source code, we recommend using
the devcontainer to avoid unnecessary / excess rebuilds.

## Acknowledgments

We would like to thank all of the following for their contributions to Dioptra,
both technical and theoretical:

- David Archer
- Rawane Issa
- James LaMar
- Hilder Vitor Lima Pereira
- Chris Phifer
