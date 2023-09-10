# Development

This section describes how to install the software within a development
sandbox on your workstation, and how to run the software tests.

## Install Sandbox
Acquire source code and install development sandbox. The authors recommend
to use a Python virtualenv.
```shell
git clone https://github.com/crate-workbench/mlflow-cratedb
cd mlflow-cratedb
python3 -m venv .venv
source .venv/bin/activate
pip install --editable='.[examples,develop,docs,test]'
```

## Software Tests
Run linters and software tests, skipping slow tests:
```shell
poe check-fast
```

Exclusively run "slow" tests.
```shell
pytest -m slow
```
