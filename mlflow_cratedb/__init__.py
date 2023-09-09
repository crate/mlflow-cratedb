from mlflow.utils import logging_utils

from mlflow_cratedb.boot import patch_all

# Enable logging, and activate monkeypatch.
logging_utils.enable_logging()
patch_all()
