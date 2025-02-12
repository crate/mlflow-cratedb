# syntax=docker/dockerfile:1

# Use BuildKit's build-time cache mounts, it makes a huge difference on rebuilds.
# - https://vsupalov.com/buildkit-cache-mount-dockerfile/
# - https://github.com/FernandoMiguel/Buildkit#mounttypecache

FROM python:3.12-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

# Install Git, it is needed for both `versioningit`, and MLflow.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

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

# 1. Install distribution packages, with caching.
# NB: installing gcc is required in order to build a wheel file
# for psutil, which is a dependency of mlflow.
# There are no binary wheel packages for psutil supporting recent
# versions of Python, thus requiring a build from source.
# psutil has a large amount of cython within its code base,
# necessitating gcc being present in the image.

# 2. Install package, with caching of dependency packages.

# 3. Uninstall distribution packages again.

# TODO: `python3-dev` will install packages for Python 3.9, typical for Debian bullseye.
#       Does this match the expectations, because the OCI is meant for Python 3.11?

RUN \
    --mount=type=cache,id=apt-cache-${TARGETARCH}${TARGETVARIANT},sharing=locked,target=/var/cache/apt \
    --mount=type=cache,id=apt-lib-${TARGETARCH}${TARGETVARIANT},sharing=locked,target=/var/lib/apt \
    --mount=type=cache,id=uv-${TARGETARCH}${TARGETVARIANT},target=/root/.cache/uv \
    true \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests --yes gcc git python3-dev \
    && uv pip install '/src' \
    && apt-get --yes remove --purge gcc git python3-dev && apt-get --yes autoremove

# Purge /src and /tmp directories.
RUN rm -rf /src /tmp/*

# Copy selftest.sh to the image
COPY release/oci-server/selftest.sh /usr/local/bin

# Run selftest.
RUN /usr/local/bin/selftest.sh
