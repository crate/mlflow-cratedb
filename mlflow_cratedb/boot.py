import logging

from mlflow_cratedb.patch.crate_python import patch_crate_python
from mlflow_cratedb.patch.mlflow import patch_mlflow

logger = logging.getLogger("mlflow")

ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


def patch_all():
    logger.info(f"{ANSI_YELLOW}Amalgamating MLflow for CrateDB{ANSI_RESET}")
    logger.debug("To undo that, run `pip uninstall mlflow-cratedb`")

    patch_crate_python()
    patch_mlflow()
