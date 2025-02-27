# Dioptra Benchmarks

This package contains a number of benchmarks of Dioptra that evaluate
Dioptra's performance.

## Installation

To be able to run the benchmarks you must first follow the following installation instructions
[`dioptra` installation instructions](../README.md#installation) and

## Available Benchmarks

The examples available for benchmarking so far:

- `perceptron`: Single perceptron -- implementation of a single percepteron with a variable number of inputs
- `matrix`: Matrix and vector multiplication implemented for several schemes

## Running the benchmarks

Each benchmark directory contains:

- Some code implementing an operation of interest to be benchmarked
- Estimation cases suitable for use with `dioptra`
- A CLI for running the computation using OpenFHE so that the actual performance can be meaured
- A script to run calibration -- `calibration.py`
- A script to run the above things with a few reasonable defaults aka `run_benchmarks.py`

