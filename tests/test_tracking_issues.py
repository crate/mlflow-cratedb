import os
import re

import mlflow
import mlflow.sklearn
from mlflow.models import Model
from mlflow.models.model import ModelInfo


def test_log_model_twice(tracking_store, reset_database):
    """
    Problem
    -------
    Problems when calling `mlflow.sklearn.log_model` twice.
    UPDATE statement on table 'registered_models' expected to update 1 row(s); 2 were matched.

    Solution
    --------
    Add a uniqueness constraint.

    References
    ----------
    - https://github.com/crate/mlflow-cratedb/issues/46
    """

    # Activate backend for tracking.
    os.environ["MLFLOW_TRACKING_URI"] = tracking_store.db_uri

    # Every experiment needs a name.
    mlflow.set_experiment("test_log_model")

    artifact_path = "testdrive-artifact"
    registered_model_name = "testdrive-artifact-model"
    sk_model = None

    # Emulate `mlflow.sklearn.log_model`.
    def log_model(metadata=None):
        return Model.log(
            artifact_path=artifact_path,
            flavor=mlflow.sklearn,
            registered_model_name=registered_model_name,
            await_registration_for=0.01,
            metadata=metadata,
            sk_model=sk_model,
        )

    # Verify that the model incurred an update.

    model_info = log_model(metadata={"status": "update-1", "training": True})
    assert isinstance(model_info, ModelInfo)
    assert re.match(r".*runs:/[0-9a-z]+/testdrive-artifact.*", model_info.model_uri)
    assert model_info.metadata == {"status": "update-1", "training": True}

    model_info = log_model(metadata={"status": "update-2", "knowledge": "excellent"})
    assert isinstance(model_info, ModelInfo)
    assert re.match(r".*runs:/[0-9a-z]+/testdrive-artifact.*", model_info.model_uri)
    assert model_info.metadata == {"status": "update-2", "knowledge": "excellent"}
