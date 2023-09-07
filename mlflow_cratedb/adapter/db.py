import importlib.resources

import sqlalchemy as sa
import sqlparse


def _setup_db_create_tables(engine: sa.Engine):
    """
    Because CrateDB does not play well with a full-fledged SQLAlchemy data model and
    corresponding Alembic migrations, shortcut that and replace it with a classic
    database schema provisioning based on SQL DDL.

    It will cause additional maintenance, but well, c'est la vie.

    TODO: Currently, the path is hardcoded to `cratedb.sql`.
    """
    schema_name = engine.url.query.get("schema")
    with importlib.resources.path("mlflow_cratedb.adapter", "ddl") as ddl:
        schema = ddl.joinpath("cratedb.sql")
        sql_statements = schema.read_text().format(schema_name=schema_name)
        with engine.connect() as connection:
            for statement in sqlparse.split(sql_statements):
                connection.execute(sa.text(statement))


def _setup_db_drop_tables():
    """
    TODO: Not implemented yet.
    """
    pass
