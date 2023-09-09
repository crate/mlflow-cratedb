from mlflow_cratedb.monkey.mlflow.model import polyfill_uniqueness_constraints
from mlflow_cratedb.monkey.mlflow.search_utils import patch_mlflow_search_utils
from mlflow_cratedb.monkey.mlflow.tracking import patch_mlflow_tracking


def patch_mlflow():
    """
    Patch the MLflow package.
    """
    polyfill_uniqueness_constraints()
    patch_mlflow_search_utils()
    patch_mlflow_tracking()
