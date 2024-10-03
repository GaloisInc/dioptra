# Dioptra: Docker

## Build

To build the image, run:

```console
> docker build -t dioptra-docker .
```

You can check that the image built successfully by running:

```console
> docker images
```

## Get a shell

After the image is built, you can create a temporary container that will be
cleaned up on exit with:

```console
> docker run --rm -it --entrypoint bash dioptra-docker
```

Note that this environment is not intended for development of `dioptra`; see
below for an alternative container option suitable for development in VSCode.

We recommend also mounting a volume to share files with the container, so you
can easily add/modify your to-be-analyzed Python files:

```console
> docker run --rm -it --entrypoint bash -v /path/to/your/files:/inputs dioptra-docker
```

## Dev Container

Inside the `.devcontainer` directory there is a devcontainer spec suitable for
development using Visual Studio Code (see https://code.visualstudio.com/docs/devcontainers/containers)
for more information.  Opening the folder using the dev container VSCode extension
should give you an environment that has OpenFHE and the Python bindings installed
globally.

## Setting up the environment

After entering a container, run `cd dioptra`, then `source setup_env.sh`. This
will:

(1) Create and enter a Python environment
(2) Build and install `dioptra_native` in that environment
(3) Install dioptra

Now, you can start using dioptra to perform FHE analyses.
