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

## Create a container

A container running JupyterLab can be started by running:

```console
> docker run -d -p 8888:8888 dioptra-docker
```

We recommend also mounting a volume to share files with the container (for
example, Python scripts to be run/analyzed by Dioptra):

```console
> docker run -d -p 8888:8888 -v /path/to/your/files:/inputs dioptra-docker
```

So shared files will be available at `/inputs`.

You can check that the container is indeed running using:

```console
> docker ps
```

## Accessing the JupyterLab

With the container running, you can navigate to
[`localhost:8888`](http://localhost:8888) to run code via the JupyterLab.

## Entering and using the container

Finally, you can access a shell in the running container with:

```console
> docker exec -it <container-name> /bin/bash
```

Where you will be in a clean `/workspace` directory where OpenFHE applications
can be cloned and run with `dioptra`, which is installed to the container for
immediate use.

# Dev Container

Inside the `.devcontainer` directory there is a devcontainer spec suitable for
development using Visual Studio Code (see https://code.visualstudio.com/docs/devcontainers/containers)
for more information.  Opening the folder using the dev container vscode extension
should give you an environment that's has OpenFHE and the python bindings installed
globally.

## Creating a virtual environment

From there, one way to continue is to create a virtual environment and install any tools you might
need so that when running `pip3 install .`, dioptra is installed in the virtual environment - 
it may not be installable otherwise.

To make a virtual environment (preferably in the `workspaces/dioptra` directory):

``` console
> python3 -mvenv .venv
```

And enter the virtual environment by:
```
> source .venv/bin/activate
```
