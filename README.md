# Dioptra: FHE Performance Estimation

TODO: Summarize Dipotra platform

## Prerequisites

Dioptra was developed using
[OpenFHE 1.1.4](https://github.com/openfheorg/openfhe-development) and
[`openfhe-python` 0.8.6](https://github.com/openfheorg/openfhe-python), the
latest versions at the time of writing. One option is to install these packages
to your system using the instructions available at the linked repositories.

Alternatively, consider installing the
[Nix package manager](https://nixos.org/download/), and running `nix-shell` at
this repository's root. This will build and install OpenFHE and the Python
bindings to your Nix store, and start a shell with a Python installation ready
to use these OpenFHE bindings. Note that as Dioptra is being developed, what is
provided in this shell may change to support the tool.

Finally, if a Docker container is preferable, see
[`docker/README.md`](docker/README.md) for instructions on building an image and
running Dioptra with it. You will need to
[install Docker](https://docs.docker.com/get-docker/) to use this, of course.

## Installation

TODO: Our tool's specific installation instructions, once we know them :)

## Quickstart

TODO: Show a small FHE script (OpenFHE example maybe?) and how to use the tool on it

## Acknowledgments

TODO: Credit ourselves, our academic partners (if appropriate), the client, etc
