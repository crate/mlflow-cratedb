import functools

import sqlalchemy as sa


def patch_db_utils():
    import mlflow.store.db.utils as db_utils

    patch_create_sqlalchemy_engine()
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


def patch_create_sqlalchemy_engine():
    """
    MLflow's SqlAlchemyStore objects invoke `_all_tables_exist()`, which in turn
    invoke SQLAlchemy Inspector's `get_table_names()`, which apparently does not
    honor the `schema` parameter.

    This leads to MLflow failing on server startup::

        mlflow.exceptions.MlflowException: Database migration in unexpected state. Run manual upgrade.
    """
    import mlflow.store.db.utils as db_utils

    create_sqlalchemy_engine_dist = db_utils.create_sqlalchemy_engine

    def create_sqlalchemy_engine(db_uri):
        from mlflow_cratedb.patch.sqlalchemy import patch_sqlalchemy_inspector

        engine = create_sqlalchemy_engine_dist(db_uri=db_uri)
        patch_sqlalchemy_inspector(engine)
        return engine

    db_utils.create_sqlalchemy_engine = create_sqlalchemy_engine
