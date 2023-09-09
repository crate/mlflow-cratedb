import mlflow
import pytest

from mlflow_cratedb import patch_all

patch_all()


# The canonical database schema used for test purposes is `testdrive`.
DB_URI = "crate://crate@localhost/?schema=testdrive"


@pytest.fixture
def testdrive_engine():
    yield mlflow.store.db.utils.create_sqlalchemy_engine_with_retry(DB_URI)
