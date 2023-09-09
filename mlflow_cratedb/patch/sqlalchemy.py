import typing as t

import sqlalchemy as sa


def patch_sqlalchemy_inspector(engine: sa.Engine):
    """
    When using `get_table_names()`, make sure the correct schema name gets used.

    TODO: Verify if this is really needed. SQLAlchemy should use the `search_path` properly already.
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
