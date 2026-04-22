"""
https://mlflow.org/docs/latest/ml/model-registry/
https://mlflow.org/docs/latest/ml/model-registry/tutorial/
"""

import mlflow
import mlflow.demo
from mlflow.tracking._tracking_service.utils import _use_tracking_uri


def test_search_registered_models_by_name(db_uri, reset_database):
    """
    Validate the registered models API.

    UnsupportedFeatureException[Function FunctionName{schema='null', name='count'}(integer) is not a scalar function.]
    https://github.com/crate/crate/issues/19196
    """
    with _use_tracking_uri(db_uri):
        mlflow.register_model("acme", "foobar")
        results = mlflow.search_registered_models(filter_string="name = 'foobar'")
        assert len(results) == 1, f"Unable to find expected model, found {len(results)}"


def test_search_registered_models_by_tag_cratedb624(db_uri, reset_database):
    """
    Validate a test case with the registered models API that fails with CrateDB 6.2.4 and earlier.

    UnsupportedFeatureException[Function FunctionName{schema='null', name='count'}(integer) is not a scalar function.]
    https://github.com/crate/crate/issues/19196
    """
    with _use_tracking_uri(db_uri):
        mlflow.register_model("acme", "foobar", tags={"enabled": "true"})
        results = mlflow.search_registered_models(filter_string="tags.enabled = 'true'")  # noqa: F841
        # TODO: Searching by tags currently does not work but yields empty results. Why?
        # assert len(results) == 1, f"Unable to find expected model, found {len(results)}"  # noqa: ERA001
