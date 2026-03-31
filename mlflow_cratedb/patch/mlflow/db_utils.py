import functools

import sqlalchemy as sa
from mlflow.store.db.utils import create_sqlalchemy_engine as create_sqlalchemy_engine_dist


def patch_db_utils():
    import mlflow.store.db.utils as db_utils

    db_utils.create_sqlalchemy_engine = create_sqlalchemy_engine
    db_utils._initialize_tables = _initialize_tables
    db_utils._verify_schema = _verify_schema


def create_sqlalchemy_engine(db_uri):
    """
    Relax OBJECT(DYNAMIC) attribute access behaviour where attribute does not exist yet.

    Example: SELECT spans.dimension_attributes['mlflow.llm.model']
    Error:   Column dimension_attributes['mlflow.llm.model'] unknown
    """
    engine = create_sqlalchemy_engine_dist(db_uri)

    def receive_engine_connect(conn):
        conn.execute(sa.text("SET error_on_unknown_object_key=false;"))
        conn.commit()

    sa.event.listen(engine, "engine_connect", receive_engine_connect)

    return engine


@functools.cache
def _initialize_tables(engine: sa.Engine):
    """
    Skip SQLAlchemy schema provisioning and Alembic migrations.
    Both don't play well with CrateDB.
    """
    from mlflow.store.db.utils import _logger

    from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables

    _logger.info("Creating initial MLflow database tables...")
    _setup_db_create_tables(engine)


def _verify_schema(engine: sa.Engine):
    """
    Skipping Alembic, that's a no-op.
    """
    pass
