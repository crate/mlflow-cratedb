# syntax=docker/dockerfile:1

# Use BuildKit's build-time cache mounts, it makes a huge difference on rebuilds.
# - https://vsupalov.com/buildkit-cache-mount-dockerfile/
# - https://github.com/FernandoMiguel/Buildkit#mounttypecache

FROM python:3.11-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

# Install Git, it is needed for both `versioningit`, and MLflow.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Copy sources
COPY . /src

# 1. Install distribution packages, with caching.
# NB: installing gcc is required in order to build a wheel file
# for psutil, which is a dependency of mlflow.
# There are no binary wheel packages for psutil supporting recent
# versions of Python, thus requiring a build from source.
# psutil has a large amount of cython within its code base,
# necessitating gcc being present in the image.

# 2. Install package, with caching of dependency packages.

# 3. Uninstall distribution packages again.

RUN \
    --mount=type=cache,id=apt,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,id=apt,sharing=locked,target=/var/lib/apt \
    --mount=type=cache,id=pip,target=/root/.cache/pip \
    true \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests --yes gcc git python3-dev \
    && pip install --use-pep517 --prefer-binary '/src' \
    && apt-get --yes remove --purge gcc git python3-dev && apt-get --yes autoremove

# Purge /src and /tmp directories.
RUN rm -rf /src /tmp/*

# Copy selftest.sh to the image
COPY release/oci-server/selftest.sh /usr/local/bin

# Run selftest.
RUN /usr/local/bin/selftest.sh
