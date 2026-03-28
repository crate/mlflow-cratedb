import logging

logger = logging.getLogger("mlflow")

ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


def patch_all():
    logger.info(f"{ANSI_YELLOW}Amalgamating MLflow for CrateDB{ANSI_RESET}")
    logger.debug("To undo that, run `pip uninstall mlflow-cratedb`")

    # Make sure SQLAlchemy is patched first, before importing any other modules.
    from mlflow_cratedb.patch.sqlalchemy import patch_sqlalchemy

    patch_sqlalchemy()

    from mlflow_cratedb.patch.mlflow import patch_mlflow
    from mlflow_cratedb.patch.pycaret import patch_pycaret

    patch_mlflow()
    patch_pycaret()
