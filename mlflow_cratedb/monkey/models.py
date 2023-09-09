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
