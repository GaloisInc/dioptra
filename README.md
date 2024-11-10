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
run `./run_examples.sh estimate`. If this produces a series of reports without
error, you are ready to use Dioptra.

## Using Dioptra

### Calibrating for your system

Dioptra bases its estimates on calibration data collected for the specific
system under test. **Important!** This step necessitates running FHE operations
many times, which can take a significant amount of time. For a given choice of
FHE scheme and parameters, however, this process only needs to be completed once
for most applications.

We provide a script, `calibrate.sh`, to simplify the process of producing
calibration data, given a Python file defining "context functions".

#### For most users

Dioptra provides an example of such a file with the following contexts defined:

- `bfv1`        (Plaintext modulus: 2^16 - 1, Multiplicative depth 2)
- `bgv1`        (ditto)
- `binfhe1`     (128-bit security)
- `ckks1`       (Uniform ternary secret key distribution, 128-bit security, Ring
                 dimension: 2^17)
- `ckks_small1` (Uniform ternary secret key distribution, INSECURE, Ring
                 dimension: 2^12)

These contexts are defined in
[the Dioptra examples](examples/src/dioptra_examples/contexts.py). From the
root of the Dioptra repository, you can produce these calibrations by running:

```console
> ./calibrate.sh examples/src/dioptra_examples/contexts.py /path/to/calibrations
```

Where `/path/to/calibrations` is the directory to which you would like the
output calibration files written. They will be named after the function defining
the context.

#### Advanced usage

You can define your own FHE contexts to be used for calibration. In
general, these will set up an OpenFHE `CryptoContext` with the proper parameters
selected (e.g. ring dimension, multiplicative depth, security level).

The following will search `/path/to/contexts.py` for functions decorated with
`@dioptra_context()` (or `@dioptra_binfhe_context()`) in a given Python file,
and report their names:

```console
> dioptra context list /path/to/contexts.py
```

Suppose you want to collect calibration data for a context named `my_ckks`
defined in `/path/to/contexts.py`. You would run the following to produce a
Dioptra calibration file for this:

```console
> dioptra context calibrate --name my_ckks \
                            --output /path/to/calibrations/my_ckks.dc \
                            /path/to/contexts.py
```

By default, 5 samples will be used during calibration. You can change this
default using `--sample-count` (or the shorter `-sc`).

Of course, once you have defined `/path/to/contexts.py`, you can use
`calibrate.sh` as above to automatically discover the decorated functions and
run calibration.

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
matrices. Furthermore, suppose we're going to set up the CKKS parameters to be
the same as those for which we earlier produced calibration data
(`my_ckks.dc`).

We can write the following function, which uses a Dioptra `Analyzer` object
where we might expect an `ofhe.CryptoContext`:

```python
@dioptra_runtime()
def matrix_mult_5x5(cc: Analyzer):
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

If this is defined in `/path/to/matrix_mult.py`, we can get an estimation report
written to the console with:

```console
> dioptra estimate report --calibration-data /path/to/calibrations/my_ckks.dc \
                          /path/to/matrix_mult.py
```

Which will output a wall-clock time estimate, and a maximum memory usage
estimate.

#### Network operations

Dioptra supports basic simulation of (homogeneous) network operations in
estimation cases. Expanding on the matrix_mult example above::

```python
@dioptra_runtime()
def matrix_mult_5x5_networked(cc: Analyzer):
    # Define the network parameters
    network = cc.MakeNetwork(
        send_bps=BPS(Mbps=100),
        recv_bps=BPS(Gbps=1),
        latency_ms=50,
    )

    rows = 5
    cols = 5

    # 'Receive' x/y ciphertexts from the network
    x_ct = [[] for _ in range(rows)]
    y_ct = [[] for _ in range(rows)]
    for i in range(rows):
        for _ in range(cols):
            ct1 = cc.ArbitraryCT()
            ct2 = cc.ArbitraryCT()

            network.RecvCiphertext(ct1)
            network.RecvCiphertext(ct2)

            x_ct[i].append(ct1)
            y_ct[i].append(ct2)

    # Compute result, and 'send' it
    res = matrix_mult(cc, x_ct, y_ct)
    network.SendCiphertext(res)
```

### Producing annotated sources

In addition to simple text reports on the console, Dioptra is capable of
creating annotated versions of your Python scripts, where estimates are shown
on a per-operation basis (per `Analyzer` operation, that is).

Like calibration, this functionality is done on a per-function basis, so you
must specify a `--name` of a function decorated with `@dioptra_runtime()`.

To invoke this functionality, run:

```console
> dioptra estimate annotate --calibration-data /path/to/calibrations/my_ckks.dc \
                            --output /path/to/annotated/matrix_mult_annotated.py \
                            --name matrix_mult_5x5 \
                            /path/to/matrix_mult.py
```

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
