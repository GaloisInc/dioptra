# Dioptra Exmples

This package contains a number of examples of Dioptra usage, including the
benchmarking examples against which Dioptra will be evaluated and refined.

## Installation

The easiest way to install this package and run all examples is using
[`run_examples.sh`](../run_examples.sh) in a Docker container obtained by
following the
[`dioptra` installation instructions](../README.md#installation).

If you have in some other way found yourself in a Python environment where
`dioptra` is installed, you can simply run:

```console
> pip install .
```

In the directory containing this `README`. This will install `dioptra_examples`
to the Python environment.

## Running the executable examples

A number of the examples are intended for benchmarking, and thus can be run in a
true FHE context for comparison against Dioptra's estimates after installation.

The examples providing such executables are:

- `dioptra_examples.boolean_binfhe`
- `dioptra_examples.matrix_mult.{bfv, bgv, ckks}`
- `dioptra_examples.nn.{bfv, bgv, ckks}`

The executable form that runs in OpenFHE can be run using, for example:

```console
> python -m dioptra_examples.matrix_mult.bfv
```
