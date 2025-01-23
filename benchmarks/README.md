# Dioptra Benchmarks

This package contains a number of benchmarks of Dioptra that evaluate
Dioptra's performance.

## Installation

To be able to run the benchmarks you must first follow the following installation instructions
[`dioptra` installation instructions](../README.md#installation) and
[`dioptra_examples` installation instructions](../examples/README.md#installation).

If you have in some other way found yourself in a Python environment where
`dioptra` is installed, you can simply run:

```console
> pip install .
```

## Available Benchmarks

The examples available for benchmarking so far:

- A single percepteron: A single percepteron with a variable number of inputs.
- A matrix x vector: A matrix vector multiplication with variable dimensions.

## Running the benchmarks

Each of the benchmarks has its own CLI and script that allow users to run thebenchmarks using the user specified settings.

For example, for the Matrix x Vector benchmark you can run:
```
python benchmarks/src/matrix_vector/run_benchmarks.py -h
```
to find the different settings that are available. Each benchmarks has a similar script and can be run in a similar fashion.
