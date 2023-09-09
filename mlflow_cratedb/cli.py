import importlib.metadata

import click

# Intercept CLI entrypoint for monkeypatching.
from mlflow.cli import cli  # noqa: F401

app_version = importlib.metadata.version("mlflow-cratedb")


@cli.command("cratedb")
@click.version_option(version=app_version)
def cratedb():
    pass
