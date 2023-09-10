#!/bin/bash

# Fail on error.
set -e

# Display all commands.
# set -x

echo "Invoking MLflow adapter for CrateDB"
python -c 'import mlflow'
python -c 'import mlflow_cratedb'
mlflow-cratedb --version
mlflow-cratedb cratedb --version
