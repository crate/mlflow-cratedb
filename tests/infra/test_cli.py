from click.testing import CliRunner

from mlflow_cratedb.cli import cli


def test_versions():
    """
    CLI test: Invoke `mlflow-cratedb --version` and `mlflow-cratedb cratedb --version`
    """
    runner = CliRunner()

    result = runner.invoke(cli, args="--version", catch_exceptions=False)
    assert result.exit_code == 0

    result = runner.invoke(cli, args="cratedb --version", catch_exceptions=False)
    assert result.exit_code == 0


def test_unknown_parameter():
    """
    CLI test: Invoke `mlflow-cratedb --foo`.
    """
    runner = CliRunner()

    result = runner.invoke(cli, args="foo", catch_exceptions=False)
    assert result.exit_code == 2
