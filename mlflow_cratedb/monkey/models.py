from mlflow_cratedb.adapter.util import generate_unique_integer


def patch_models():
    """
    Configure SQLAlchemy model columns with an alternative to `autoincrement=True`.

    In this case, use a random identifier: Nagamani19, a short, unique,
    non-sequential identifier based on Hashids.

    TODO: Submit patch to `crate-python`, to be enabled by a
          dialect parameter `crate_translate_autoincrement` or such.
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
