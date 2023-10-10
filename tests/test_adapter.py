import pytest
import sqlalchemy as sa
from mlflow.store.tracking.dbmodels.initial_models import Base
from mlflow.store.tracking.dbmodels.models import SqlExperiment
from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore

from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables, _setup_db_drop_tables

ARTIFACT_URI = "artifact_folder"


@pytest.fixture
def store(engine: sa.Engine):
    """
    A fixture for providing an instance of `SqlAlchemyStore`.
    """
    yield SqlAlchemyStore(str(engine.url), ARTIFACT_URI)


@pytest.fixture
def store_empty(store):
    """
    A fixture for providing an instance of `SqlAlchemyStore`,
    after pruning all database tables.
    """
    with store.ManagedSessionMaker() as session:
        session.query(SqlExperiment).delete()
        for mapper in Base.registry.mappers:
            session.query(mapper.class_).delete()
            # FIXME: `testdrive` is hardcoded here.
            sql = f"REFRESH TABLE testdrive.{mapper.class_.__tablename__};"
            session.execute(sa.text(sql))
    yield store


def test_setup_tables(engine: sa.Engine):
    """
    Test if creating database tables works, and that they use the correct schema.
    """
    _setup_db_drop_tables(engine=engine)
    _setup_db_create_tables(engine=engine)
    with engine.connect() as connection:
        result = connection.execute(sa.text("SELECT * FROM testdrive.experiments;"))
        assert result.rowcount == 0


def test_query_model(store: SqlAlchemyStore):
    """
    Verify setting up MLflow database tables works well.
    """

    with store.ManagedSessionMaker() as session:
        # Verify table has one record, the "Default" experiment.
        assert session.query(SqlExperiment).count() == 1

        # Run a basic ORM-based query.
        experiment: SqlExperiment = session.query(SqlExperiment).one()
        assert experiment.name == "Default"

        # Run the same query using plain SQL.
        # This makes sure the designated schema is properly used through `search_path`.
        record = session.execute(sa.text("SELECT * FROM testdrive.experiments;")).mappings().one()
        assert record["name"] == "Default"
