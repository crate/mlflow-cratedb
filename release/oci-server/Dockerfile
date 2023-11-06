# syntax=docker/dockerfile:1

# Use BuildKit's build-time cache mounts, it makes a huge difference on rebuilds.
# - https://vsupalov.com/buildkit-cache-mount-dockerfile/
# - https://github.com/FernandoMiguel/Buildkit#mounttypecache

FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Install Git, it is needed for both `versioningit`, and MLflow.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install distribution packages, with caching.
# NB: installing gcc is required in order to build a wheel file
# for psutil, which is a dependency of mlflow.
# The binaries for psutil do not support Python 3.10, requiring
# a build from source. psutil has a large amount of cython within
# its code base, necessitating gcc being present in the image.
RUN \
    --mount=type=cache,id=apt,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,id=apt,sharing=locked,target=/var/lib/apt \
    true \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests --yes gcc git python3-dev

# Copy sources
COPY . /src

# Install package, with caching of dependency packages.
RUN \
    --mount=type=cache,id=pip,target=/root/.cache/pip \
    true \
    && pip install --use-pep517 --prefer-binary '/src'

# Uninstall distribution packages again.
# TODO: Optimize - previous layers have already been written.
RUN apt-get --yes remove --purge gcc git python3-dev && apt-get --yes autoremove

# Purge /src and /tmp directories.
RUN rm -rf /src /tmp/*

# Copy selftest.sh to the image
COPY release/oci-server/selftest.sh /usr/local/bin

# Run selftest.
RUN /usr/local/bin/selftest.sh
