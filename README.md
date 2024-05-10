# Dioptra: FHE Performance Estimation

TODO: Summarize Dipotra platform

## Installation

**Disclaimer:** The following has only been tested on Darwin/OSX and Linux
systems, and there is no intention to support Windows at this time.
If you encounter any problems, please let us know!

### In a fresh system environment

The `dioptra` platform can be installed directly to your system with relative
ease. The following assumes you have at least Python 3.9 installed.

First, clone
[the OpenFHE repository](https://github.com/openfheorg/openfhe-development) and
follow the instructions
[here](https://openfhe-development.readthedocs.io/en/latest/sphinx_rsts/intro/installation/installation.html)
to install for your platform (Linux or MacOS).

For simplicity, we recommend that GMP, NTL, and tcmalloc **not** be installed.
GMP/NTL have almost the same performance as the default backends for all
schemes, and tcmalloc improves performance only when `OMP_NUM_THREADS > 1`. In
this "building from scratch" case, you are free to utilize these features; but
take note that the Nix and Docker options described below do not use these
features.

Next, we recommend creating a Python virtual environment to use for OpenFHE
development (or a suitable alternative, such as a `conda` environment). For
convenience, you can clone this repo and create the virtual environment at its
root (`python -m venv .venv`). Activate the environment
(`source .venv/bin/activate` in most cases).

Follow the instructions to install
[`openfhe-python`](https://github.com/openfheorg/openfhe-python). This will
install the OpenFHE Python bindings to your virtual environment, which are
required by `dioptra` (despite not being captured as a dependency in
`pyproject.toml`).

Finally, run `pip install .` (or `pip install -e .` if you're a developer) at
the root of this repository. This will install the `dioptra` binary to your
virtual environment. In cases where you already have an environment suitable for
building and running OpenFHE Python applications, this step is all that's
required to install the `dioptra` platform.

### Nix shell

We have included Nix expressions to package `openfhe-development` and
`openfhe-python` in the `nix/` directory. Note that these may become obsolete, if
these packages are added to `NixOS/nixpkgs`. This would clean up this repository
quite significantly, since the packages could be fetched directly from the
`nixpkgs` repository.

Running `nix-shell` at the repository root will drop you into an environment
with a Python installation suitable for OpenFHE development, a small handful of
Python static analysis tools (`mypy` and `ruff`), and the `dioptra` platform.
No complicated install steps needed; this should "just work".

The [Nix package manager](https://nixos.org/download/) is the only other
requirement to take advantage of this.

### Docker

See [the Docker README](README.Docker.md) for build/use details. Containers
provide a JupyterLab web interface to build and run OpenFHE applications, and
the `dioptra` platform is installed to be used interactively with shared volumes
or scripts cloned to the container.

## Quickstart

TODO: Show a small FHE script (OpenFHE example maybe?) and how to use the tool on it

## Acknowledgments

TODO: Credit ourselves, our academic partners (if appropriate), the client, etc
