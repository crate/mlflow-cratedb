import typing as t

import sqlalchemy as sa


def patch_db_utils():
    import mlflow.store.db.utils as db_utils

    db_utils._initialize_tables = _initialize_tables
    db_utils._verify_schema = _verify_schema


def _initialize_tables(engine: sa.Engine):
    """
    Skip SQLAlchemy schema provisioning and Alembic migrations.
    Both don't play well with CrateDB.
    """
    from mlflow.store.db.utils import _logger

    from mlflow_cratedb.adapter.db import _setup_db_create_tables

    patch_sqlalchemy_inspector(engine)
    _logger.info("Creating initial MLflow database tables...")
    _setup_db_create_tables(engine)


def _verify_schema(engine: sa.Engine):
    """
    Skipping Alembic, that's a no-op.
    """
    pass


def patch_sqlalchemy_inspector(engine: sa.Engine):
    """
    When using `get_table_names()`, make sure the correct schema name gets used.

    TODO: Submit this to SQLAlchemy?
    """
    get_table_names_dist = engine.dialect.get_table_names
    schema_name = engine.url.query.get("schema")
    if isinstance(schema_name, tuple):
        schema_name = schema_name[0]

    def get_table_names(connection: sa.Connection, schema: t.Optional[str] = None, **kw: t.Any) -> t.List[str]:
        if schema is None:
            schema = schema_name
        return get_table_names_dist(connection=connection, schema=schema, **kw)

    engine.dialect.get_table_names = get_table_names  # type: ignore
