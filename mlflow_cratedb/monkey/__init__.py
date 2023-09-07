import logging

from mlflow_cratedb.monkey.db_types import patch_dbtypes
from mlflow_cratedb.monkey.db_utils import patch_db_utils
from mlflow_cratedb.monkey.environment_variables import patch_environment_variables
from mlflow_cratedb.monkey.models import patch_models
from mlflow_cratedb.monkey.server import patch_run_server
from mlflow_cratedb.monkey.tracking import patch_sqlalchemy_store

logger = logging.getLogger("mlflow")

ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


def patch_all():
    logger.info(f"{ANSI_YELLOW}Amalgamating MLflow for CrateDB{ANSI_RESET}")
    logger.debug("To undo that, run `pip uninstall mlflow-cratedb`")

    patch_environment_variables()
    patch_models()
    patch_sqlalchemy_store()
    patch_dbtypes()
    patch_db_utils()
    patch_run_server()
