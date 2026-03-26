# syntax=docker/dockerfile:1

# Use BuildKit's build-time cache mounts, it makes a huge difference on rebuilds.
# - https://vsupalov.com/buildkit-cache-mount-dockerfile/
# - https://github.com/FernandoMiguel/Buildkit#mounttypecache

FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

# Copy sources
COPY . /src

# Enable concurrent multi-arch builds.
# https://github.com/docker/buildx/issues/549#issuecomment-1788297892
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT

# Configure build environment.
ENV PIP_ROOT_USER_ACTION=ignore
ENV UV_COMPILE_BYTECODE=true
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_SYSTEM_PYTHON=true

# Install the `uv` package manager.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy example programs and documentation to the image.
COPY examples /opt/ml/bin
COPY docs /opt/ml/docs

# Install Git, it is needed for both `versioningit`, and MLflow.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN \
    --mount=type=cache,id=apt-cache-${TARGETARCH}${TARGETVARIANT},sharing=locked,target=/var/cache/apt \
    --mount=type=cache,id=apt-lib-${TARGETARCH}${TARGETVARIANT},sharing=locked,target=/var/lib/apt \
    --mount=type=cache,id=uv-${TARGETARCH}${TARGETVARIANT},target=/root/.cache/uv \
    true \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests --yes build-essential git openjdk-17-jre \
    && uv pip install '/src' --requirements=/src/examples/requirements.txt

# Purge /src and /tmp directories.
RUN rm -rf /src /tmp/*

# Copy selftest.sh to the image
COPY release/oci-runtime/selftest.sh /usr/local/bin

# Run selftest.
RUN /usr/local/bin/selftest.sh
