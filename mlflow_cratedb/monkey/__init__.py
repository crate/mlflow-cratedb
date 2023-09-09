import logging

from mlflow_cratedb.monkey.db_types import patch_dbtypes
from mlflow_cratedb.monkey.db_utils import patch_db_utils
from mlflow_cratedb.monkey.environment_variables import patch_environment_variables
from mlflow_cratedb.monkey.mlflow import patch_mlflow
from mlflow_cratedb.monkey.models import patch_compiler, patch_models
from mlflow_cratedb.monkey.server import patch_run_server
from mlflow_cratedb.patch.crate_python import patch_raise_for_status

logger = logging.getLogger("mlflow")

ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


def patch_all():
    logger.info(f"{ANSI_YELLOW}Amalgamating MLflow for CrateDB{ANSI_RESET}")
    logger.debug("To undo that, run `pip uninstall mlflow-cratedb`")

    # crate-python
    patch_raise_for_status()

    # MLflow
    patch_environment_variables()
    patch_compiler()
    patch_models()
    patch_dbtypes()
    patch_db_utils()
    patch_mlflow()
    patch_run_server()
