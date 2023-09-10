from mlflow_cratedb.patch.mlflow.db_types import patch_dbtypes
from mlflow_cratedb.patch.mlflow.db_utils import patch_db_utils
from mlflow_cratedb.patch.mlflow.model import polyfill_refresh_after_dml, polyfill_uniqueness_constraints
from mlflow_cratedb.patch.mlflow.search_utils import patch_search_utils
from mlflow_cratedb.patch.mlflow.server import patch_run_server
from mlflow_cratedb.patch.mlflow.settings import patch_environment_variables
from mlflow_cratedb.patch.mlflow.tracking import patch_tracking


def patch_mlflow():
    """
    Patch the MLflow package.
    """
    patch_dbtypes()
    patch_db_utils()
    polyfill_refresh_after_dml()
    polyfill_uniqueness_constraints()
    patch_run_server()
    patch_environment_variables()
    patch_search_utils()
    patch_tracking()
