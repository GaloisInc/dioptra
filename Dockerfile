# Ubuntu with some prompting disabled
FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

# Essential packages
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    sudo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Python tools we need
RUN pip3 install --no-cache-dir \
                 "pybind11[global]" \
                 jupyterlab \
                 build \
                 mypy \
                 ruff \
                 pytest \
                 --break-system-packages

# OpenFHE C++ bindings
RUN git clone https://github.com/openfheorg/openfhe-development.git \
    && cd openfhe-development \
    && mkdir build \
    && cd build \
    && cmake -DBUILD_UNITTESTS=OFF -DBUILD_EXAMPLES=OFF -DBUILD_BENCHMARKS=OFF .. \
    && make -j$(nproc) \
    && make install
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}

# OpenFHE Python bindings
RUN git clone https://github.com/openfheorg/openfhe-python.git \
    && cd openfhe-python \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install

# Install Dioptra
WORKDIR /dioptra
COPY pyproject.toml .
COPY src/ .
COPY README.md .
RUN pip3 install . --break-system-packages

# Move to a fresh workspace
WORKDIR /workspace

# Jupyterlab port & default command
EXPOSE 8888
CMD ["jupyter-lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.allow_origin='*'", "--NotebookApp.password=''", "--NotebookApp.password_required=False"]
