# MLflow adapter for CrateDB


## About

A wrapper around [MLflow] to use [CrateDB] as storage database for [MLflow Tracking].


## Setup

Install the most recent version of the `mlflow-cratedb` package.
```shell
pip install --upgrade 'git+https://github.com/crate-workbench/mlflow-cratedb'
```


## Usage

TODO.


## Development

Acquire source code and install development sandbox.
```shell
git clone https://github.com/crate-workbench/mlflow-cratedb
cd mlflow-cratedb
python3 -m venv .venv
source .venv/bin/activate
pip install --editable='.[develop,docs,test]'
```

Run linters and software tests:
```shell
source .venv/bin/activate
poe check
```


[CrateDB]: https://github.com/crate/crate
[CrateDB Cloud]: https://console.cratedb.cloud/
[MLflow]: https://mlflow.org/
[MLflow Tracking]: https://mlflow.org/docs/latest/tracking.html
