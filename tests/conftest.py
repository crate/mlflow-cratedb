import os

import pytest

from mlflow_cratedb import patch_all

patch_all()

import mlflow
import mlflow.store.tracking.sqlalchemy_store as mlflow_tracking
import sqlalchemy as sa

ARTIFACT_URI = "testdrive_folder"


@pytest.fixture(autouse=True)
def reset_environment() -> None:
    """
    Make sure software tests do not pick up any environment variables.
    """
    if "MLFLOW_TRACKING_URI" in os.environ:
        del os.environ["MLFLOW_TRACKING_URI"]


@pytest.fixture
def db_uri() -> str:
    """
    The canonical database schema used for testing purposes is `testdrive`.
    """
    return "crate://crate@localhost/?schema=testdrive"


@pytest.fixture
def engine(db_uri):
    """
    Provide an SQLAlchemy engine object using the `testdrive` schema.
    """
    yield mlflow.store.db.utils.create_sqlalchemy_engine_with_retry(db_uri)


@pytest.fixture
def tracking_store(engine: sa.Engine) -> mlflow_tracking.SqlAlchemyStore:
    """
    A fixture for providing an instance of `SqlAlchemyStore`.
    """
    yield mlflow_tracking.SqlAlchemyStore(str(engine.url), ARTIFACT_URI)


@pytest.fixture
def reset_database(engine: sa.Engine):
    """
    Make sure to reset the database by dropping and re-creating tables.
    """
    from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables, _setup_db_drop_tables

    _setup_db_drop_tables(engine=engine)
    _setup_db_create_tables(engine=engine)
