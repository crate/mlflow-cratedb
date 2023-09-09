import importlib.resources

import sqlalchemy as sa
import sqlparse
from sqlalchemy.event import listen


def _setup_db_create_tables(engine: sa.Engine):
    """
    Because CrateDB does not play well with a full-fledged SQLAlchemy data model and
    corresponding Alembic migrations, shortcut that and replace it with a classic
    database schema provisioning based on SQL DDL.

    It will cause additional maintenance, but well, c'est la vie.

    TODO: Currently, the path is hardcoded to `cratedb.sql`.
    """
    schema_name = engine.url.query.get("schema")
    schema_prefix = ""
    if schema_name is not None:
        schema_prefix = f'"{schema_name}".'
    with importlib.resources.path("mlflow_cratedb.adapter", "ddl") as ddl:
        sql_file = ddl.joinpath("cratedb.sql")
        sql_statements = sql_file.read_text().format(schema_prefix=schema_prefix)
        with engine.connect() as connection:
            for statement in sqlparse.split(sql_statements):
                connection.execute(sa.text(statement))


def _setup_db_drop_tables():
    """
    TODO: Not implemented yet.
    """
    pass


def enable_refresh_after_dml():
    """
    Run `REFRESH TABLE <tablename>` after each INSERT, UPDATE, and DELETE operation.

    CrateDB is eventually consistent, i.e. write operations are not flushed to
    disk immediately, so readers may see stale data. In a traditional OLTP-like
    application, this is not applicable.

    This SQLAlchemy extension makes sure that data is synchronized after each
    operation manipulating data.

    TODO: Submit patch to `crate-python`, to be enabled by a
          dialect parameter `crate_dml_refresh` or such.
    """
    from mlflow.store.db.base_sql_model import Base

    for mapper in Base.registry.mappers:
        listen(mapper.class_, "after_insert", do_refresh)
        listen(mapper.class_, "after_update", do_refresh)
        listen(mapper.class_, "after_delete", do_refresh)


def do_refresh(mapper, connection, target):
    """
    SQLAlchemy event handler for `after_{insert,update,delete}` events, invoking `REFRESH TABLE`.
    """
    sql = f"REFRESH TABLE {target.__tablename__}"
    connection.execute(sa.text(sql))
