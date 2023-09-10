#!/bin/bash

# Fail on error.
set -e

# Display all commands.
# set -x

echo "Import ML libraries"
python -c 'import merlion'
python -c 'import mlflow'

# Print installed software versions.
java --version
mlflow --version
