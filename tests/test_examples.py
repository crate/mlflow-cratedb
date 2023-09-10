import logging
import sys
import time
from pathlib import Path

import mlflow
import pytest
import sqlalchemy as sa

from mlflow_cratedb.adapter.setup_db import _setup_db_create_tables, _setup_db_drop_tables
from tests.util import process

# The canonical database schema used for example purposes is `examples`.
DB_URI = "crate://crate@localhost/?schema=examples"
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"


logger = logging.getLogger(__name__)


@pytest.fixture
def engine():
    yield mlflow.store.db.utils.create_sqlalchemy_engine_with_retry(DB_URI)


def test_tracking_merlion(engine: sa.Engine):
    _setup_db_drop_tables(engine=engine)
    _setup_db_create_tables(engine=engine)
    tracking_merlion = Path(__file__).parent.parent.joinpath("examples").joinpath("tracking_merlion.py")
    cmd_server = [
        "mlflow-cratedb",
        "server",
        "--workers=1",
        f"--backend-store-uri={DB_URI}",
        "--gunicorn-opts='--log-level=debug'",
    ]
    cmd_client = [
        sys.executable,
        tracking_merlion,
    ]

    logger.info("Starting server")
    with process(cmd_server, stdout=sys.stdout.buffer, stderr=sys.stderr.buffer, close_fds=True) as server_process:
        logger.info(f"Started server with process id: {server_process.pid}")
        # TODO: Wait for HTTP response.
        time.sleep(4)
        logger.info("Starting client")
        with process(
            cmd_client,
            env={"MLFLOW_TRACKING_URI": MLFLOW_TRACKING_URI},
            stdout=sys.stdout.buffer,
            stderr=sys.stderr.buffer,
        ) as client_process:
            client_process.wait(timeout=120)
            assert client_process.returncode == 0

    # TODO: Verify database content.
