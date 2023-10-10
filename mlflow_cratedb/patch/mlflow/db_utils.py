import functools

import sqlalchemy as sa


def patch_db_utils():
    import mlflow.store.db.utils as db_utils

    db_utils._initialize_tables = _initialize_tables
    db_utils._verify_schema = _verify_schema


@functools.cache
def _initialize_tables(engine: sa.Engine):
    """
    Skip SQLAlchemy schema provisioning and Alembic migrations.
    Both don't play well with CrateDB.
    """
    from mlflow.store.db.utils import _logger

    from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables

    _logger.info("Creating initial MLflow database tables...")
    _setup_db_create_tables(engine)


def _verify_schema(engine: sa.Engine):
    """
    Skipping Alembic, that's a no-op.
    """
    pass
