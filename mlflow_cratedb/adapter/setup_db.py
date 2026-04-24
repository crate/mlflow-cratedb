import importlib.resources
from typing import cast

import sqlalchemy as sa
import sqlparse


def read_ddl(filename: str):
    return importlib.resources.files("mlflow_cratedb.adapter.ddl").joinpath(filename).read_text()


def _setup_db_create_tables(engine: sa.Engine):
    """
    Because CrateDB does not play well with a full-fledged SQLAlchemy data model and
    corresponding Alembic migrations, shortcut that and replace it with a classic
    database schema provisioning based on SQL DDL.

    It will cause additional maintenance, but well, c'est la vie.

    TODO: Currently, the path is hardcoded to `cratedb.sql`.
    """
    sql_statements = read_ddl("cratedb.sql")
    with engine.connect() as connection:
        for statement in sqlparse.split(sql_statements):
            connection.execute(sa.text(statement))
        connection.commit()


def _setup_db_drop_tables(engine: sa.Engine):
    """
    Drop all relevant database tables. Handle with care.
    """
    sql_statements = read_ddl("drop.sql")
    with engine.connect() as connection:
        for statement in sqlparse.split(sql_statements):
            connection.execute(sa.text(statement))
        connection.commit()


def _get_schema(engine: sa.Engine) -> str:
    """Get schema from SQLAlchemy connection URL."""
    schema = cast(str, engine.url.query.get("schema"))
    if not schema:
        raise ValueError("No schema specified")
    if schema == "doc":
        raise ValueError("Schema is `doc`. Will not operate on that.")
    return schema


def _setup_db_drop_schema(engine: sa.Engine):
    """Drop all relevant database tables by dropping schema. Handle with care."""
    schema = _get_schema(engine)
    with engine.connect() as connection:
        connection.execute(sa.text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))  # noqa: S608
        connection.commit()


def _setup_db_truncate_tables(engine: sa.Engine):
    """Delete data from all relevant database tables. Handle with care."""
    schema = _get_schema(engine)
    with engine.connect() as connection:
        inspector = sa.inspect(engine)
        all_tables = inspector.get_table_names(schema=schema)
        for table in all_tables:
            connection.execute(sa.text(f'DELETE FROM "{table}"'))  # noqa: S608
            connection.execute(sa.text(f'REFRESH TABLE "{table}"'))  # noqa: S608
        connection.commit()
