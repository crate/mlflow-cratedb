from abc import ABC

from mlflow_cratedb.adapter.util import generate_unique_integer


def patch_models():
    """
    Configure SQLAlchemy model columns with an alternative to `autoincrement=True`.

    In this case, use a random identifier: Nagamani19, a short, unique,
    non-sequential identifier based on Hashids.
    """
    import sqlalchemy as sa
    import sqlalchemy.sql.schema as schema

    ColumnDist: type = schema.Column

    class Column(ColumnDist, ABC):
        inherit_cache = False

        def __init__(self, *args, **kwargs):
            if "autoincrement" in kwargs:
                del kwargs["autoincrement"]
                if "default" not in kwargs:
                    kwargs["default"] = generate_unique_integer
            ColumnDist.__init__(self, *args, **kwargs)  # type: ignore

    schema.Column = Column  # type: ignore
    sa.Column = Column  # type: ignore
