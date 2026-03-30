# Intercept server entrypoint for monkeypatching.
# ruff: noqa: ERA001

# Use Flask with gunicorn
# from mlflow.server import app  # noqa: F401

# Use FastAPI with uvicorn
from mlflow.server.fastapi_app import app  # noqa: F401
