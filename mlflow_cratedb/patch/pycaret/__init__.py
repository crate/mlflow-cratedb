from mlflow_cratedb.patch.pycaret.mlflow_logger import patch_logger


def patch_pycaret():
    """
    Patch the PyCaret package.
    """
    patch_logger()
