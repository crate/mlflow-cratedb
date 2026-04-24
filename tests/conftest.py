import logging
import os
import subprocess
import sys
from typing import Any, Generator

import pytest

from mlflow_cratedb import patch_all
from tests.util import process, wait_for_server

patch_all()

import sqlalchemy as sa
from mlflow import MlflowClient
from mlflow.store.model_registry.sqlalchemy_store import SqlAlchemyStore as ModelRegistrySqlAlchemyStore
from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore as TrackingSqlAlchemyStore
from mlflow.store.workspace.sqlalchemy_store import SqlAlchemyStore as WorkspaceSqlAlchemyStore

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
    import sqlalchemy as sa
    from mlflow.store.db.utils import create_sqlalchemy_engine
    from sqlalchemy_cratedb.support import quote_relation_name

    url = sa.make_url(db_uri)
    schema = url.query.get("schema")

    engine = create_sqlalchemy_engine(db_uri)

    if schema is not None:

        def receive_engine_connect(conn):
            """Configure search path, so all database connections always use the right schema."""
            conn.execute(sa.text(f"SET search_path={quote_relation_name(schema)};"))
            conn.commit()

        sa.event.listen(engine, "engine_connect", receive_engine_connect)

    yield engine


@pytest.fixture
def model_registry_store(engine: sa.Engine, reset_database) -> Generator[ModelRegistrySqlAlchemyStore, Any, None]:
    """
    A fixture for providing an instance of `ModelRegistrySqlAlchemyStore`.
    """
    yield ModelRegistrySqlAlchemyStore(str(engine.url))


@pytest.fixture
def tracking_store(
    engine: sa.Engine, artifact_uri: str, reset_database
) -> Generator[TrackingSqlAlchemyStore, Any, None]:
    """
    A fixture for providing an instance of `TrackingSqlAlchemyStore`.
    """
    yield TrackingSqlAlchemyStore(str(engine.url), artifact_uri)


@pytest.fixture
def workspace_store(engine: sa.Engine, reset_database) -> Generator[WorkspaceSqlAlchemyStore, Any, None]:
    """
    A fixture for providing an instance of `WorkspaceSqlAlchemyStore`.
    """
    yield WorkspaceSqlAlchemyStore(str(engine.url))


@pytest.fixture
def reset_database(engine: sa.Engine):
    """
    Make sure to reset the database by dropping and re-creating tables.

    With dropping and re-creating all the tables each time,
    `poe test-fast` takes whopping 781.84s. Let's just apply
    a `DELETE FROM <table>` procedure going forward, which is
    much cheaper (138.97s for `poe test-fast`).
    """
    from mlflow_cratedb.adapter.setup_db import (
        _setup_db_create_tables,
        _setup_db_truncate_tables,
    )

    # Variant 1: Drop and re-create tables.
    """
    _setup_db_drop_schema(engine=engine)
    _setup_db_drop_tables(engine=engine)
    """
    # Variant 2: Truncate tables.
    _setup_db_truncate_tables(engine=engine)

    # Ensure tables exist.
    _setup_db_create_tables(engine=engine)


@pytest.fixture(scope="session")
def mlflow_server(db_uri: str, tracking_uri: str) -> Generator[subprocess.Popen, Any, None]:
    cmd_server = [
        "mlflow-cratedb",
        "server",
        "--workers=1",
        f"--backend-store-uri={db_uri}",
        "--uvicorn-opts=--log-level=debug",
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


@pytest.fixture
def tracking_canvas(db_uri, reset_database):
    """Set up MLflow tracking URI and reset database before each test case."""
    from mlflow.tracking._tracking_service.utils import _use_tracking_uri

    with _use_tracking_uri(db_uri):
        yield
