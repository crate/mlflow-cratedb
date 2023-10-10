# Usage

This documentation section explains how to use this software successfully,
please read it carefully.


## Introduction

The repository includes a few [example programs](../examples), which can be used
to exercise the MLflow setup, and to get started.

The `MLFLOW_TRACKING_URI` environment variable defines whether to record outcomes
directly into the database, or by submitting them to an MLflow Tracking Server.

```shell
# Use CrateDB database directly
export MLFLOW_TRACKING_URI="crate://crate@localhost/?schema=mlflow"

# Use MLflow Tracking Server
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```


## CrateDB Cluster

You can exercise the examples both with a local instance of CrateDB, or
by using a database cluster on [CrateDB Cloud]. 

### CrateDB on localhost

In order to spin up a CrateDB instance without further ado, you can use Docker
or Podman.
```shell
docker run --rm -it \
  --name=cratedb --publish=4200:4200 --publish=5432:5432 \
  --env=CRATE_HEAP_SIZE=4g crate \
  -Cdiscovery.type=single-node
```

For the subsequent examples to work out of the box, please define those
environment variables.
```shell
export CRATEDB_HTTP_URL="http://localhost:4200"
export CRATEDB_SQLALCHEMY_URL="crate://crate@localhost:4200/?schema=mlflow"
```

### CrateDB Cloud

When using [CrateDB Cloud], define those environment variables instead.
```shell
export CRATEDB_USERNAME="admin"
export CRATEDB_PASSWORD="<PASSWORD>"
export CRATEDB_HTTP_URL="https://${CRATEDB_USERNAME}:${CRATEDB_PASSWORD}@example.aks1.westeurope.azure.cratedb.net:4200"
export CRATEDB_SQLALCHEMY_URL="crate://${CRATEDB_USERNAME}:${CRATEDB_PASSWORD}@example.aks1.westeurope.azure.cratedb.net:4200/?ssl=true&schema=mlflow"
```


## Run Experiment

### Standalone

In order to instruct MLflow to submit the experiment metadata directly to CrateDB,
configure the `MLFLOW_TRACKING_URI` environment variable to point to your CrateDB
server.

```shell
export MLFLOW_TRACKING_URI="crate://crate@localhost/?schema=mlflow"
python examples/tracking_dummy.py
```

### Tracking Server

Start the MLflow server, pointing it to your CrateDB instance.
By default, it will listen on port 5000, serving the HTTP API
and the web UI, see http://localhost:5000/.

```shell
mlflow-cratedb server --backend-store-uri="${CRATEDB_SQLALCHEMY_URL}" --dev
```

In order to instruct MLflow to submit the experiment metadata to the MLflow Tracking
Server, configure the `MLFLOW_TRACKING_URI` environment variable to point to its
HTTP endpoint.

```shell
export MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
python examples/tracking_dummy.py
```


## Operations

You can use `crash` to inquire the relevant MLflow database tables.
```shell
crash --hosts="${CRATEDB_HTTP_URL}" --schema=mlflow --command='SELECT * FROM "experiments";'
crash --hosts="${CRATEDB_HTTP_URL}" --schema=mlflow --command='SELECT * FROM "runs";'
```

You can also use `crash` to manually run the provided SQL DDL statements.
```shell
crash --hosts="${CRATEDB_HTTP_URL}" --schema=mlflow < mlflow_cratedb/adapter/ddl/cratedb.sql
crash --hosts="${CRATEDB_HTTP_URL}" --schema=mlflow < mlflow_cratedb/adapter/ddl/drop.sql
```


## Remarks

For running the MLflow server, you need to invoke the `mlflow-cratedb` command, which
runs MLflow amalgamated with the necessary changes to support CrateDB.

In the same spirit, when running standalone programs, make sure to import the `mlflow_cratedb`
module, in order to bring in the needed amalgamations to make MLflow work with CrateDB.
It can be inspected within the `examples/tracking_dummy.py` program.
```python
def start_adapter():
    logger.info("Initializing CrateDB adapter")
    import mlflow_cratedb  # noqa: F401
```

Also note that we recommend to use a dedicated schema for storing MLflow's
tables, for example `"mlflow"`. In that spirit, CrateDB's default schema
`"doc"` is not populated by any tables of 3rd-party systems.

If you want to run the MLflow adapter for CrateDB on a container infrastructure,
please refer to the [container usage](./container.md) documentation.
