# Container Usage

The project operates GHA workflows to build and publish two OCI images to
GHCR, `mlflow-cratedb` and `ml-runtime`.

- `ghcr.io/crate/mlflow-cratedb`
  Includes the amalgamated Mlflow for CrateDB adapter, ready to run.
  Effectively, it contains the same packages as if you installed them with
  `pip install 'mlflow-cratedb'`

- `ghcr.io/crate/ml-runtime`
  Includes a few popular machine learning libraries and other software
  to support your experiments. Effectively, it contains the same packages
  as if you installed them with `pip install 'mlflow-cratedb[examples]'`.

For general usage information, please refer to the [handbook](./handbook.md).
For building your own images, see the [development documentation](./development.md).
On GHCR, other than `latest` images for releases, there are also images for
each PR, as well as `nightly` ones.

On GHCR, you will find the following image tags:
- `latest`: Points to the most recent release.
- `main`: Builds of `main`, when pushing to this branch.
- `nightly`: Builds of `main`, each morning a 4 o'clock CEST.


## Docker and Podman

This section demonstrates how to use the OCI images using Docker. Podman
can also be used by replacing the `docker` command with `podman`.


### Prerequisites

The following command line examples for both "Standalone" and "Tracking Server"
variants have been written to use a CrateDB instance running on `localhost`.
This command starts it, also using Docker.

```shell
docker run --rm -it \
  --name=cratedb --publish=4200:4200 --publish=5432:5432 \
  --env=CRATE_HEAP_SIZE=4g crate \
  -Cdiscovery.type=single-node
```


### Standalone

In order to instruct MLflow to submit the experiment metadata directly to CrateDB,
configure the `MLFLOW_TRACKING_URI` environment variable to point to your CrateDB
server. When running the experiment within a container, instead of using `localhost`,
you will need to address the CrateDB container by name instead.

```shell
docker run --rm -it --link=cratedb \
  --env="MLFLOW_TRACKING_URI=crate://crate@cratedb:4200/?schema=mlflow" \
  --env="CRATEDB_HTTP_URL=http://crate@cratedb:4200/?schema=doc" \
  ghcr.io/crate/ml-runtime python /opt/ml/bin/tracking_dummy.py
```

You can use `crash` to inquire the relevant MLflow database tables.
```shell
docker run --rm -it --link=cratedb ghcr.io/crate/ml-runtime \
  crash --hosts="http://crate@cratedb:4200/" --schema=mlflow --command='SELECT * FROM "experiments";'
docker run --rm -it --link=cratedb ghcr.io/crate/ml-runtime \
  crash --hosts="http://crate@cratedb:4200/" --schema=mlflow --command='SELECT * FROM "runs";'
```


### Tracking Server

When running the MLflow Server within a container, you will need to address the
CrateDB container by name instead of using `localhost`.

```shell
export CRATEDB_SQLALCHEMY_URL="crate://crate@cratedb:4200/?schema=mlflow"
```

Start the MLflow Server, linking it to the other container running CrateDB,
and exposing its HTTP port 5000 to your machine, serving the HTTP API
and the web UI, see http://localhost:5000/.

```shell
docker run --rm -it --name=mlflow --link=cratedb --publish=5000:5000 \
  ghcr.io/crate/mlflow-cratedb mlflow-cratedb server \
  --backend-store-uri="${CRATEDB_SQLALCHEMY_URL}" --host=0.0.0.0 \
  --gunicorn-opts="--log-level=debug"
```

Start an experiment program which needs to access both CrateDB and MLflow,
for storing data and recording experiment metadata, linking it to both
other containers.

```shell
docker run --rm -it --link=cratedb --link=mlflow \
  --env="MLFLOW_TRACKING_URI=http://mlflow:5000" \
  --env="CRATEDB_HTTP_URL=http://crate@cratedb:4200/?schema=doc" \
  ghcr.io/crate/ml-runtime python /opt/ml/bin/tracking_merlion.py
```


## Kubernetes

Todo.
