# Dioptra: FHE Performance Estimation

TODO: Summarize Dipotra platform

## Prerequisites

**Disclaimer:** The following has only been tested on Darwin/OSX and Linux
systems. If you encounter any problems, please let us know!

Installing Dioptra natively requires an installation of
[`openfhe-python`](https://github.com/openfheorg/openfhe-python) be present in
the Python environment before installation. Please follow the installation
instructions in that repository to install these bindings to your system before
attempting to install and use Dioptra locally.

Alternatively, consider installing the
[Nix package manager](https://nixos.org/download/), and running `nix-shell` at
this repository's root. This will build and install OpenFHE and the Python
bindings to your Nix store, and start a shell with a Python installation ready
to use these OpenFHE bindings, as well as the `dioptra` executable which can
immediately be used to run/analyze OpenFHE applications.

Finally, if a Docker container is preferable, see
[`README.Docker.md`](README.Docker.md) for instructions on building the Dioptra
Docker image, running a container with JupyterLab and Dioptra ready to use,
and accessing a shell within the container to clone OpenFHE applications / if
no browser is available to use the JupyterLab.

Using either of these alternative approaches, the following section on
Installation can be skipped.

## Installation (System)

First, make sure that the OpenFHE Python bindings have been properly installed.
An easy way to check is to start a Python interpreter, and run:

```python
from openfhe import *
```

If no errors are reported, you're good to go.

If you don't have it already, install `build`:

```console
> pip install --upgrade build
```

(Note that you may need to use `pip3` instead.)

Then, run:

```console
> python -m build
```

(As before, you may need to use `python3` instead.)

This will generate a directory `dist`, containing a `.whl` file. If you wish to
install Dioptra to your system, you can `pip install` this wheel:

```console
> pip install dist/dioptra-0.0.1-py3-none-any.whl
```

Which will automatically make the `dioptra` binary available on your `$PATH`.

## Quickstart

TODO: Show a small FHE script (OpenFHE example maybe?) and how to use the tool on it

## Acknowledgments

TODO: Credit ourselves, our academic partners (if appropriate), the client, etc
