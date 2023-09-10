import logging
import sys
import time
from pathlib import Path

import pytest
import sqlalchemy as sa
from mlflow.store.tracking.dbmodels.models import SqlExperiment, SqlMetric, SqlParam
from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore

from tests.util import process

# The test cases within this file exercise two different ways of recording
# ML experiments. They can either be directly submitted to the database,
# or alternatively to an MLflow Tracking Server.
MLFLOW_TRACKING_URI_SERVER = "http://127.0.0.1:5000"


logger = logging.getLogger(__name__)


def get_example_program_path(filename: str):
    """
    Compute path to example program.
    """
    return Path(__file__).parent.parent.joinpath("examples").joinpath(filename)


@pytest.mark.examples
def test_tracking_dummy(reset_database, engine: sa.Engine, tracking_store: SqlAlchemyStore, db_uri):
    """
    Run a dummy experiment program, without any data.
    Verify that the database has been populated appropriately.

    Here, no MLflow Tracking Server is used, so the `MLFLOW_TRACKING_URI`
    will be the SQLAlchemy database connection URI, i.e. the program will
    directly communicate with CrateDB.

    -- https://mlflow.org/docs/latest/tracking.html#backend-stores
    """

    # Invoke example program.
    tracking_dummy = get_example_program_path("tracking_dummy.py")
    logger.info("Starting experiment program")
    with process(
        [sys.executable, tracking_dummy],
        env={"MLFLOW_TRACKING_URI": db_uri},
        stdout=sys.stdout.buffer,
        stderr=sys.stderr.buffer,
    ) as client_process:
        client_process.wait(timeout=10)
        assert client_process.returncode == 0

    # Verify database content.
    with tracking_store.ManagedSessionMaker() as session:
        assert session.query(SqlExperiment).count() == 2
        assert session.query(SqlMetric).count() == 4
        assert session.query(SqlParam).count() == 5


@pytest.mark.examples
def test_tracking_merlion(reset_database, engine: sa.Engine, tracking_store: SqlAlchemyStore, db_uri):
    """
    Run a real experiment program, reporting to an MLflow Tracking Server.
    Verify that the database has been populated appropriately.

    Here, `MLFLOW_TRACKING_URI` will be the HTTP URL of the Tracking Server,
    i.e. the program will submit events and metrics to it, wrapping the
    connection to CrateDB.
    """
    tracking_merlion = get_example_program_path("tracking_merlion.py")
    cmd_server = [
        "mlflow-cratedb",
        "server",
        "--workers=1",
        f"--backend-store-uri={db_uri}",
        "--gunicorn-opts='--log-level=debug'",
    ]
    cmd_client = [
        sys.executable,
        tracking_merlion,
    ]

    logger.info("Starting server")
    with process(cmd_server, stdout=sys.stdout.buffer, stderr=sys.stderr.buffer, close_fds=True) as server_process:
        logger.info(f"Started server with process id: {server_process.pid}")
        # TODO: Wait for HTTP response.
        time.sleep(4)

        # Invoke example program.
        logger.info("Starting client")
        with process(
            cmd_client,
            env={"MLFLOW_TRACKING_URI": MLFLOW_TRACKING_URI_SERVER},
            stdout=sys.stdout.buffer,
            stderr=sys.stderr.buffer,
        ) as client_process:
            client_process.wait(timeout=120)
            assert client_process.returncode == 0

    # Verify database content.
    with tracking_store.ManagedSessionMaker() as session:
        assert session.query(SqlExperiment).count() == 2
        assert session.query(SqlMetric).count() == 4
        assert session.query(SqlParam).count() == 5
