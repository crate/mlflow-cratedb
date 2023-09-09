def patch_crate_python():
    patch_compiler()
    patch_models()
    patch_raise_for_status()


def patch_models():
    """
    Configure SQLAlchemy model columns with an alternative to `autoincrement=True`.

    In this case, use a random identifier: Nagamani19, a short, unique,
    non-sequential identifier based on Hashids.

    TODO: Submit patch to `crate-python`, to be enabled by a
          dialect parameter `crate_polyfill_autoincrement` or such.
    """
    import sqlalchemy.sql.schema as schema

    init_dist = schema.Column.__init__

    def __init__(self, *args, **kwargs):
        if "autoincrement" in kwargs:
            del kwargs["autoincrement"]
            if "default" not in kwargs:
                kwargs["default"] = generate_unique_integer
        init_dist(self, *args, **kwargs)

    schema.Column.__init__ = __init__  # type: ignore[method-assign]


def patch_compiler():
    """
    Patch CrateDB SQLAlchemy dialect to not omit the `FOR UPDATE` clause on
    `SELECT ... FOR UPDATE` statements.

    https://github.com/crate-workbench/mlflow-cratedb/issues/7

    TODO: Submit to `crate-python` as a bugfix patch.
    """
    from crate.client.sqlalchemy.compiler import CrateCompiler

    def for_update_clause(self, select, **kw):
        return ""

    CrateCompiler.for_update_clause = for_update_clause


def patch_raise_for_status():
    """
    Patch the `crate.client.http._raise_for_status` function to properly raise
    SQLAlchemy's `IntegrityError` exceptions for CrateDB's `DuplicateKeyException`
    errors.

    It is needed to make the `check_uniqueness` machinery work, which is emulating
    UNIQUE constraints on table columns.

    https://github.com/crate-workbench/mlflow-cratedb/issues/9

    TODO: Submit to `crate-python` as a bugfix patch.
    """
    import crate.client.http as http

    _raise_for_status_dist = http._raise_for_status

    def _raise_for_status(response):
        from crate.client.exceptions import IntegrityError, ProgrammingError

        try:
            return _raise_for_status_dist(response)
        except ProgrammingError as ex:
            if "DuplicateKeyException" in ex.message:
                raise IntegrityError(ex.message, error_trace=ex.error_trace) from ex
            raise

    http._raise_for_status = _raise_for_status


def check_uniqueness_factory(sa_entity, attribute_name):
    """
    Run a manual column value uniqueness check on a table, and raise an IntegrityError if applicable.

    CrateDB does not support the UNIQUE constraint on columns. This attempts to emulate it.

    TODO: Submit patch to `crate-python`, to be enabled by a
          dialect parameter `crate_polyfill_unique` or such.
    """

    def check_uniqueness(mapper, connection, target):
        from sqlalchemy.exc import IntegrityError

        if isinstance(target, sa_entity):
            # TODO: How to use `session.query(SqlExperiment)` here?
            stmt = (
                mapper.selectable.select()
                .filter(getattr(sa_entity, attribute_name) == getattr(target, attribute_name))
                .compile(bind=connection.engine)
            )
            results = connection.execute(stmt)
            if results.rowcount > 0:
                raise IntegrityError(
                    statement=stmt,
                    params=[],
                    orig=Exception(f"DuplicateKeyException on column: {target.__tablename__}.{attribute_name}"),
                )

    return check_uniqueness


def generate_unique_integer() -> int:
    """
    Produce a short, unique, non-sequential identifier based on Hashids.
    """
    from vasuki import generate_nagamani19_int

    return generate_nagamani19_int(size=10)
