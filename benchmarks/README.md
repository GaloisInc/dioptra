# Dioptra Benchmarks

This package contains a number of benchmarks of Dioptra that evaluate
Dioptra's performance.

## Hardware Requirements

To actually run the benchmarks using OpenFHE with the default settings you will
need a machine with at least 64G of memory and a pretty powerful processor will
be necessary to execute them in a reasonable amount of time - the default calibration
data was collected on a laptop with:

Processor: 13th Gen Intel(R) Core(TM) i9-13900HX
Memory: 64G

## Installation

To be able to run the benchmarks you must first follow the following installation instructions
[`dioptra` installation instructions](../README.md#installation) and

## Available Benchmarks

The examples available for benchmarking so far:

- `perceptron`: Single perceptron -- implementation of a single perceptron with a variable number of inputs
- `matrix`: Matrix and vector multiplication implemented for several schemes
- `int_comparison`: Integer comparison - determine if a two lists of integers have any common elements
                    or if every element of one list is less that the corresponding element in the other 

## Running the benchmarks

Each benchmark directory contains:

- Some code implementing an operation of interest to be benchmarked
- Estimation cases suitable for use with `dioptra`
- A CLI for running the computation using OpenFHE so that the actual performance can be meaured
- A script to run calibration -- `calibration.py`
- A script to run the above things with a few reasonable defaults aka `run_benchmarks.py`

