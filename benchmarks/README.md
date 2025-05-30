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
- `information_retrieval`: Private information retreival - look up a value by an index without revealing what
                           anything about the index or result

## Running the benchmarks

Each benchmark directory contains:

- Some code implementing an operation of interest to be benchmarked
- Estimation cases suitable for use with `dioptra`
- A CLI for running the computation using OpenFHE so that the actual performance can be meaured
- A script to run calibration -- `calibrate.py`
- A script to run the above things with a few reasonable defaults aka `run_benchmarks.py`

## Notes about the benchmarks

These benchmarks are chiefly interested in measuing the _latency_ of OpenFHE programs since this
is what Dioptra is able to measure, but many of the algorithms implemented in the PKE schemes are 
generally _batched_ so in comparing implementations of these algorithms it might be important also 
to consider _thoroughput_ for some applications.

Also note that some of the contexts are set up for configurations intended to be similar to 
OpenFHE's examples. For example, the evaluation key infrastructure needed for bootstrapping
might be set up even if bootstraping is ultimately not used in the algorithm in question.  
Changing these parameters may have a dramatic effect, particularly on memory usage.

The BinFHE benchmarks are also slower both to run and to estimate mainly because they
are performing many bit level operations serially while the PKE examples are more able
to use the parallelism of the host machine (via OpenFHE using OpenMP.)  It's possible
that the BinFHE benchmarks could be an order of magnitude faster if parallelism
were to be introduced.
