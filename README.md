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

Once installed, the easiest way to get started is to explore `dioptra --help`
and the `--help` option for all sub-commands. In general, you will need to run:

1. `dioptra context calibrate ...` to generate calibration data from an
   appropriately-decorated function (note that `dioptra context list` is a
   useful command to run first, as this will list the decorated functions in
   the given Python source file, whose names you will need to run calibration).
2. `dioptra estimate report ...` with your generated calibration data, and a
   Python source. Note that the scheme of the calibration must match the scheme
   of the actual Python source we care to analyze!
3. `dioptra estimate annotate ...` if you would like to generate new source
   files containing annotation comments showing more granular performance data,
   so it is easier to see where time is being spent in your application.

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

TODO: NCSC distribution statement, if applicable?
