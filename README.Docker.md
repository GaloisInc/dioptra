# Dioptra: Docker

## Build

To build the image, run:

```console
> docker build -t dioptra-docker .
```

This should be run from within the `docker` directory (where you are now!).

You can check that the image built successfully by running:

```console
> docker images
```

## Create a container

A container running jupyterlab in the background can be created by running:

```console
> docker run -d -p 8888:8888 dioptra-docker
```

We recommend also mounting a volume to share files with the container (for
example, Python scripts to be run/analyzed by Dioptra):

```console
> docker run -d -p 8888:8888 -v /path/to/your/files:/inputs dioptra-docker
```

You can check that the container is indeed running using:

```console
> docker ps
```

## Accessing the jupyterlab

With the container running, you can navigate to
[`localhost:8888`](http://localhost:8888) to run code via the jupyterlab.

## Entering and using the container

Finally, you can access a shell in the running container with:

```console
> docker exec -it <container-name> /bin/bash
```

TODO: Details on how to run Dioptra within the container.

The OpenFHE libraries are available within the container, so packages that
depend on them may be cloned and run/used without any need for manual
installation. If the container was created using `-v`, local files can be shared
with the container to be analyzed with Dioptra.
