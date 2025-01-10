# Dioptra Benchmarks

This package contains a number of benchmarks of Dioptra that evaluate
Dioptra's performance.

## Installation

The easiest way to install this package and run all benchmarks is by
following the
[`dioptra` installation instructions](../README.md#installation) and
[`dioptra_examples` installation instructions](../examples/README.md#installation), then running
[`./run_benchmarks.sh <estimate|execute>`](../run_examples.sh) in the resulting
Docker container.

If you have in some other way found yourself in a Python environment where
`dioptra` is installed, you can simply run:

```console
> pip install .
```

In the directory containing this `README`. This will install `dioptra_benchmarks`
to the Python environment.

## Running the executable benchmarks

A number of the examples are intended for benchmarking, and thus can be run in a
true FHE context for comparison against Dioptra's estimates after installation.

The examples providing such executables are:

- `dioptra_benchmarks.perceptron <NUM_INPUTS>`

The executable form that runs in OpenFHE can be run using, for example:

```console
> python -m dioptra_benchmarks.perceptron <NUM_INPUTS>
```

Where <NUM_INPUTS> refers to the number of inputs to the benchmark specified by the user.

