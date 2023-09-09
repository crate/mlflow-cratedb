import importlib.resources

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


def _setup_db_drop_tables(engine: sa.Engine):
    """
    Drop all relevant database tables. Handle with care.
    """
    sql_statements = read_ddl("drop.sql")
    with engine.connect() as connection:
        for statement in sqlparse.split(sql_statements):
            connection.execute(sa.text(statement))
