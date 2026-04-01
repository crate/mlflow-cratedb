import logging
import os
import subprocess
import sys
from typing import Any, Generator

import pytest
from mlflow import MlflowClient

from mlflow_cratedb import patch_all
from tests.util import process, wait_for_server

patch_all()

import mlflow
import mlflow.store.tracking.sqlalchemy_store as mlflow_tracking
import sqlalchemy as sa

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def reset_environment() -> None:
    """
    Make sure software tests do not pick up any environment variables.
    """
    if "MLFLOW_TRACKING_URI" in os.environ:
        del os.environ["MLFLOW_TRACKING_URI"]


@pytest.fixture(scope="session")
def artifact_uri() -> str:
    """
    The canonical location where artifacts are stored.
    """
    return "artifact_folder"


@pytest.fixture(scope="session")
def db_uri() -> str:
    """
    The canonical database schema used for testing purposes is `testdrive`.
    """
    return "crate://crate@localhost/?schema=testdrive"


@pytest.fixture(scope="session")
def tracking_uri() -> str:
    """
    The canonical MLflow tracking URI.

    The test cases exercise two different ways of recording ML experiments.
    They can either be directly submitted to the database,
    or alternatively to an MLflow Tracking Server.
    """
    return "http://127.0.0.1:5000"


@pytest.fixture
def engine(db_uri: str):
    """
    Provide an SQLAlchemy engine object using the `testdrive` schema.
    """
    yield mlflow.store.db.utils.create_sqlalchemy_engine_with_retry(db_uri)


@pytest.fixture
def tracking_store(engine: sa.Engine, artifact_uri: str) -> Generator[mlflow_tracking.SqlAlchemyStore, Any, None]:
    """
    A fixture for providing an instance of `SqlAlchemyStore`.
    """
    yield mlflow_tracking.SqlAlchemyStore(str(engine.url), artifact_uri)


@pytest.fixture
def reset_database(engine: sa.Engine):
    """
    Make sure to reset the database by dropping and re-creating tables.
    """
    from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables, _setup_db_drop_tables

    schema = engine.url.query.get("schema")
    if False and schema and schema != "doc":
        with engine.connect() as conn:
            conn.execute(sa.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
    else:
        _setup_db_drop_tables(engine=engine)
    _setup_db_create_tables(engine=engine)


@pytest.fixture(scope="session")
def mlflow_server(db_uri: str, tracking_uri: str) -> Generator[subprocess.Popen, Any, None]:
    cmd_server = [
        "mlflow-cratedb",
        "server",
        "--workers=1",
        f"--backend-store-uri={db_uri}",
        "--uvicorn-opts='--log-level=debug'",
    ]

    logger.info("Starting server")
    with process(cmd_server, stdout=sys.stdout.buffer, stderr=sys.stderr.buffer, close_fds=True) as server_process:
        logger.info(f"Started server with process id: {server_process.pid}")
        wait_for_server(f"{tracking_uri}/health")
        yield server_process


@pytest.fixture(scope="session")
def mlflow_client(tracking_uri: str) -> MlflowClient:
    return MlflowClient(
        tracking_uri=tracking_uri,
        # TODO: Does the model registry also work with CrateDB?
        registry_uri=None,
    )
