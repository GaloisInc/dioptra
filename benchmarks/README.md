# Dioptra Benchmarks

This package contains a number of benchmarks of Dioptra that evaluate
Dioptra's performance.

## Installation

To be able to run the benchmarks you must first follow the following installation instructions
[`dioptra` installation instructions](../README.md#installation) and
[`dioptra_examples` installation instructions](../examples/README.md#installation).

## Available Benchmarks

The examples available for benchmarking so far:

- A single percepteron: A single percepteron with a variable number of inputs.
- A matrix x vector: A matrix vector multiplication with variable dimensions.

## Running the benchmarks

Each benchmark directory contains:

- Some code implementing an operation of interest to be benchmarked
- Estimation cases suitable for use with `dioptra`
- A CLI for running the computation using OpenFHE so that the actual performance can be meaured
- A script to run the above things with a few reasonable defaults

For example, for the Matrix x Vector benchmark you can run:

```
python benchmarks/src/matrix_vector/run_benchmarks.py -h
```

to find the different settings that are available. Each benchmark has a similar script and can be run in a similar fashion.
