import mlflow

from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables, _setup_db_drop_tables


def test_all_tables_exist(testdrive_engine):
    """
    Cover `patch_sqlalchemy_inspector`: SQLAlchemy's Inspector
    needs a patch to honor the `schema` parameter.
    """
    _setup_db_drop_tables(engine=testdrive_engine)
    assert mlflow.store.db.utils._all_tables_exist(testdrive_engine) is False
    _setup_db_create_tables(engine=testdrive_engine)
    assert mlflow.store.db.utils._all_tables_exist(testdrive_engine) is True
